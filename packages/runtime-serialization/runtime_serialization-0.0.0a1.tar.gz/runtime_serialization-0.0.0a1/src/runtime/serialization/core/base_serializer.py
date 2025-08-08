from __future__ import annotations
from typing import Generic, TypeVar, Type, Sequence, MutableSequence, Mapping, MutableMapping, Any, cast
from collections import abc
from typingutils import AnyType, UnionParameter, TypeParameter, TypeArgs, get_generic_arguments, get_type_name, isinstance_typing, issubclass_typing, is_union, is_variadic_tuple_type
from typingutils.internal import get_generic_origin, get_union_types

from runtime.serialization.core.threading import Lock
from runtime.serialization.core.helpers import is_primitive, construct_generic_type
from runtime.serialization.core.shared import is_serializable
from runtime.serialization.core.decorators.type_resolving.dict_object import DictObject
from runtime.serialization.core.decorators.type_resolving.resolve_as_decorator import resolve
from runtime.serialization.core.serializer_attributes import SerializerAttributes, serialize_type, SERIALIZABLE_TYPE_DEFS
from runtime.serialization.core.interfaces.serializer_attributes import SerializerAttributes as SerializerAttributesInterface
from runtime.serialization.core.interfaces.formatter import Formatter
from runtime.serialization.core.member import Member
from runtime.serialization.core.not_serializable_exception import NotSerializableException
from runtime.serialization.core.deserialization_exception import DeserializationException
from runtime.serialization.core.serialization_exception import SerializationException
from runtime.serialization.core.circular_reference_exception import CircularReferenceException
from runtime.serialization.core.primitives import PrimitiveMapping, Primitives, Primitive

T = TypeVar('T')

TYPE_DESCRIPTOR = "~type"
VALUE_DESCRIPTOR = "~value"

class BaseSerializer(Generic[T]):
    __slots__ = ["__attributes", "__formatter", "__formatter_type"]
    __serializer_cache_lock__ = Lock()
    __serializer_cache__: dict[tuple[type[Any], type[Formatter]], BaseSerializer[Any]] = {}
    __attributes: SerializerAttributesInterface

    def __new__(cls, formatter: type[Formatter], *args: Any, **kwargs: Any):
        serializable, *_ = cast(tuple[type[Any]], get_generic_arguments(cls))
        key = (serializable, formatter)

        with BaseSerializer.__serializer_cache_lock__:
            if key not in BaseSerializer.__serializer_cache__:
                instance = object.__new__(cls)
                instance.__attributes = SerializerAttributes.get(serializable)
                BaseSerializer.__serializer_cache__[key] = instance
                return instance
        return BaseSerializer.__serializer_cache__[key]

    def __init__(self, formatter: type[Formatter]):
        self.__formatter_type = formatter
        self.__formatter = formatter()


    @property
    def attributes(self) -> SerializerAttributesInterface:
        return self.__attributes

    @property
    def formatter(self) -> Formatter:
        return self.__formatter


    def serialize(
        self,
        obj: T, /,
        base: type[T] | None = None,
    ) -> PrimitiveMapping:
        """Serializes the object to a basic dictionary

        Args:
            obj (T): The object to serialize
            base (type[T]): The base type

        Returns:
            Mapping[str, Any]: A dictionary
        """

        return self.__serialize(obj, base = base)

    def __serialize(
        self,
        obj: T, /,
        base: type[T] | None = None,
        stack: MutableSequence[Any] | None = None,
        path: str = "root"
    ) -> PrimitiveMapping:
        stack = stack or []
        if type(obj) is self.attributes.serializable:
            null_members: Sequence[Member] = [
                member for member in self.attributes.members
                if member.get_value(obj) is None
            ]

            injected_members: Mapping[Member, Any] = {}
            if self.attributes.injector:
                recur = True
                while null_members and recur:
                    recur = False
                    for member in null_members:
                        value, success = self.attributes.injector.try_inject_null_property(self.attributes.serializable, member)
                        if success:
                            null_members = [ null_member for null_member in null_members if null_member != member ]
                            injected_members[member] = value
                            recur = True
                            break

            null_members: Sequence[Member] = [
                member for member in null_members
                if not member.is_nullable
            ]

            if len(null_members) > 0:
                null_properties_str = "', '".join([ member.name for member in null_members ])
                raise SerializationException(f"Cannot serialize object of type '{serialize_type(type(obj))}', because the value of following non-nullable members are NULL: '{null_properties_str}'", path)

            if self.attributes.strict:
                selected_members = self.attributes.members
            else:
                selected_members = [
                    member
                    for member in self.attributes.members
                    if not member.is_nullable or member.get_value(obj) is not None or member in injected_members
                ]

            if hasattr(obj, "__hash__"):
                if obj in stack:
                    raise CircularReferenceException(stack[0], stack[-1], f"'{path}'")
                else:
                    stack.append(obj)
            else:
                pass # pragma: no cover

            data = {
                member.name : injected_members[member] if member in injected_members else self.__serialize_member(member, obj, stack, f"{path}.{member.name}")
                for member in selected_members
            }

            if not base or base is not type(obj):
                type_str = serialize_type(type(obj))
                data[TYPE_DESCRIPTOR] = type_str

            return data
        elif self.attributes.is_resolvable:
            derived_serializer = BaseSerializer[type(obj)](self.__formatter_type)
            return derived_serializer.__serialize(
                obj,
                base = type(obj),
                stack = stack,
                path = path
            )
        elif isinstance(obj,  self.attributes.serializable):
            derived_serializer = BaseSerializer[type(obj)](self.__formatter_type)
            return derived_serializer.__serialize(
                obj,
                stack = stack,
                path = path
            )
        else:
            raise NotSerializableException(type(obj)) # pragma: no cover

    def __serialize_member(self, member: Member, obj: Any, stack: MutableSequence[Any], path: str) -> Primitives:
        value = member.get_value(obj)

        if self.attributes.strict:
            if not member.return_type or not isinstance_typing(value, member.return_type, recursive = True):
                raise SerializationException(f"Cannot serialize object '{get_type_name(self.attributes.serializable)}' because member '{member.name}' value type is different from '{member.return_type}'", path)

        return self.__serialize_value(value, member.return_type, stack, path)

    def __serialize_value(self, value: Any, member_type: AnyType | None, stack: MutableSequence[Any], path: str) -> Primitives:
        serialized: Primitives | None = None
        value_type: AnyType = type(value) # pyright: ignore[reportUnknownVariableType]
        generic_args: tuple[AnyType, ...] = ()
        serialized_member_type: AnyType | None = member_type
        is_serializable_member = member_type and is_serializable(member_type)

        if member_type is not None:
            generic_args = get_generic_arguments(member_type)

        if isinstance(value, tuple):
            serialized, serialized_member_type = self.__serialize_tuple(cast(tuple[Any, ...], value), generic_args, member_type, stack, path)
        elif isinstance(value, list):
            serialized, serialized_member_type = self.__serialize_list(cast(list[Any], value), generic_args, member_type, stack, path)
        elif isinstance(value, set):
            serialized, serialized_member_type = self.__serialize_set(cast(set[Any], value), generic_args, member_type, stack, path)
        elif isinstance(value, abc.Mapping):
            serialized, serialized_member_type = self.__serialize_dict(cast(abc.Mapping[Any, Any], value), generic_args, member_type, stack, path)

        if serialized is not None:
            encoded, result = self.__formatter.encode(serialized, serialized_member_type)
            if result:
                return encoded
            else:
                return serialized
        else:
            formatter_type = cast(AnyType, member_type if member_type is not None or self.attributes.strict or value is None else type(value)) # pyright: ignore[reportUnknownArgumentType]
            encoded, result = self.__formatter.encode(value, formatter_type)

            if result:
                if type(encoded) is member_type:
                    return encoded
                elif member_type is not None and issubclass_typing(type(encoded), member_type):
                    return encoded
                elif member_type is not None and member_type not in (type[Any], Type[Any]) and issubclass_typing(value_type, member_type):
                    return encoded
                else:
                    return {
                        TYPE_DESCRIPTOR: serialize_type(value_type),
                        VALUE_DESCRIPTOR: encoded
                    }
            elif member_type is not None and not isinstance_typing(value, member_type):
                raise SerializationException(f"Value '{value}' cannot be serialized as {get_type_name(member_type)}", path)

            # elif not self.attributes.strict and not is_serializable(value): # try to make serializable
            #     create_serializer(value_type, self.__formatter_type, deserializer=DefaultDeserializer, strict=self.attributes.strict, injector=self.attributes.injector)

            if member_type is not None:
                if issubclass_typing(value_type, member_type) and is_union(member_type):
                    # member_type might be a union, so serialize as value_type
                    serializer = cast(BaseSerializer[Any], BaseSerializer[value_type](self.__formatter_type))
                    serialized = serializer.__serialize(cast(Any, value), base = value_type, stack = stack, path = path)
                    non_primitive_union_types = [ t for t in get_union_types(cast(UnionParameter, member_type)) if not is_primitive(t) ]
                    add_type_hint = False

                    if len(non_primitive_union_types) == 1: # primitive types doesn't need type hints
                        serializer = SerializerAttributes.get(non_primitive_union_types[0])
                        if non_primitive_union_types[0] == value_type:
                            pass
                        elif serializer.is_resolvable:
                            pass
                        else:
                            add_type_hint = True

                    if add_type_hint:
                        cast(MutableMapping[str, Any], serialized)[TYPE_DESCRIPTOR] = serialize_type(value_type)

                    return serialized

                elif is_serializable_member and not is_union(member_type):
                    root = SerializerAttributes.get(member_type)
                    generic_type = cast(type[Any], value_type if root.is_resolvable else member_type)
                    serializer = BaseSerializer[generic_type](self.__formatter_type)

                    return serializer.__serialize(
                        cast(Any, value),
                        base = cast(type[Any], value_type if root.is_resolvable else member_type),
                        stack = stack,
                        path = path
                    )
                elif not self.attributes.strict and not is_serializable_member: # try to make serializable
                    SerializerAttributes.make_serializable(cast(type[Any], member_type))
                    serializer = BaseSerializer[cast(type[Any], member_type)](self.__formatter_type)
                    return serializer.__serialize(cast(Any, value), base = cast(type[Any], member_type), stack = stack, path = path)
                else:
                    pass # pragma: no cover

            if not self.attributes.strict:
                generic_type = cast(type[Any], type(value)) # pyright: ignore[reportUnknownArgumentType]
                serializer = BaseSerializer[generic_type](self.__formatter_type)
                return serializer.__serialize(cast(Any, value), stack = stack, path = path)

            raise NotSerializableException(cast(type[Any], type(value))) # pyright: ignore[reportUnknownArgumentType] # pragma: no cover

    def __serialize_tuple(self, value: tuple[Any, ...], generic_args: TypeArgs, member_type: AnyType | None, stack: MutableSequence[Any], path: str) -> tuple[Primitives, AnyType]:
        is_variadic = member_type and is_variadic_tuple_type(cast(type[tuple[Any, ...]], member_type))
        variadic_type = generic_args[0] if generic_args and is_variadic else None

        if not any(cast(tuple[Any], value)):
            serialized = []
        elif generic_args and not is_variadic:
            serialized_list: Sequence[Any] = []
            for index, (generic_type, item) in enumerate(zip(generic_args, value)):
                try:
                    serialized_list.append(self.__serialize_value(item, generic_type, stack, path))
                except SerializationException as ex:
                    raise SerializationException(ex.error, f"{path}[{index}]") from ex
            serialized = serialized_list
        else:
            serialized_list: Sequence[Any] = []
            for index, item in enumerate(value):
                try:
                    serialized_list.append(self.__serialize_value(item, variadic_type, stack, path))
                except SerializationException as ex: # pragma: no cover
                    raise SerializationException(ex.error, f"{path}[{index}]") from ex
            serialized = serialized_list

        return serialized, list

    def __serialize_list(self, value: list[Any], generic_args: TypeArgs, member_type: AnyType | None, stack: MutableSequence[Any], path: str) -> tuple[Primitives, AnyType]:
        if not any(value):
            serialized = []
        elif generic_args and len(generic_args) == 1:
            serialized_list: Sequence[Any] = []
            for index, item in enumerate(value):
                try:
                    serialized_list.append(self.__serialize_value(item, generic_args[0], stack, path))
                except SerializationException as ex:
                    raise SerializationException(ex.error, f"{path}[{index}]") from ex
            serialized = serialized_list
        else:
            serialized_list: Sequence[Any] = []
            for index, item in enumerate(value):
                try:
                    serialized_list.append(self.__serialize_value(item, None, stack, path))
                except SerializationException as ex: # pragma: no cover
                    raise SerializationException(ex.error, f"{path}[{index}]") from ex
            serialized = serialized_list

        return serialized, member_type or list

    def __serialize_set(self, value: set[Any], generic_args: TypeArgs, member_type: AnyType | None, stack: MutableSequence[Any], path: str) -> tuple[Primitives, AnyType]:
        if not any(value):
            serialized = []
        elif generic_args and len(generic_args) == 1:
            serialized_list: Sequence[Any] = []
            for index, item in enumerate(cast(Sequence[Any], value)):
                try:
                    serialized_list.append(self.__serialize_value(item, generic_args[0], stack, path))
                except SerializationException as ex: # pragma: no cover
                    raise SerializationException(ex.error, f"{path}[{index}]") from ex
            serialized = serialized_list
        else:
            serialized_list: Sequence[Any] = []
            for index, item in enumerate(cast(Sequence[Any], value)):
                try:
                    serialized_list.append(self.__serialize_value(item, None, stack, path))
                except SerializationException as ex: # pragma: no cover
                    raise SerializationException(ex.error, f"{path}[{index}]") from ex
            serialized = serialized_list

        return serialized, list

    def __serialize_dict(self, value: abc.Mapping[Any, Any], generic_args: TypeArgs, member_type: AnyType | None, stack: MutableSequence[Any], path: str) -> tuple[Primitives, AnyType]:
        if not any(value):
            serialized = {}
        elif generic_args and len(generic_args) == 2:
            generic_key_type, generic_value_type = generic_args
            serialized_dict: Mapping[Any, Any] = {}
            for key, dvalue in value.items():
                try:
                    serialized_dict[self.__serialize_value(key, generic_key_type, stack, path)] = self.__serialize_value(dvalue, generic_value_type, stack, path)
                except SerializationException as ex: # pragma: no cover
                    raise SerializationException(ex.error, f"{path}{{{key}}}") from ex
            serialized = serialized_dict
        else:
            serialized_dict: Mapping[Any, Any] = {}
            for key, dvalue in value.items():
                try:
                    if not isinstance(key, (bool, int, float, str)):
                        raise SerializationException("Untyped dicts can only have primitive keys e.g. strings, ints and/or floats.", f"{path}{{{key}}}")
                    serialized_dict[key] = self.__serialize_value(dvalue, None, stack, f"{path}{{{key}}}")
                except SerializationException as ex: # pragma: no cover
                    raise SerializationException(ex.error, f"{path}{{{key}}}") from ex


            serialized = serialized_dict

        return serialized, member_type or dict


    def deserialize(self, data: PrimitiveMapping) -> T:
        """Deserializes a dictionary to an object

        Args:
            data (Mapping): The data to deserialize

        Returns:
            T: An object
        """
        return self.__deserialize(data)

    def __deserialize(self, data: PrimitiveMapping, path: str = "root") -> T:
        if TYPE_DESCRIPTOR in data:
            data_type, unwrapped = unwrap(data)

            if not issubclass_typing(data_type, self.attributes.serializable):
                raise DeserializationException(f"Type '{serialize_type(data_type)}' is not derived from '{serialize_type(self.attributes.serializable)}'", path)
            elif not is_serializable(data_type):
                raise DeserializationException(f"Type '{serialize_type(data_type)}' is not serializable", path) from NotSerializableException(data_type)

            return self.__get_serializer(cast(type[Any], data_type), self.__formatter_type).deserialize(unwrapped)
        else:
            if self.attributes.is_resolvable:
                data_deserialized = {
                    member.name: self.__deserialize_member(member, data, f"{path}.{member.name}")
                    for member in self.attributes.members
                    if not isinstance(member.member_type, (list, dict, tuple, set))
                }
                data_obj = DictObject(data_deserialized)
                serializable = resolve(self.attributes.serializable, data_obj)
                derived_serializer = cast(BaseSerializer[T], BaseSerializer[serializable](self.__formatter_type))
                return derived_serializer.deserialize(data)

            null_members = [
                member for member in self.attributes.members
                if member.name not in data or data[member.name] is None
            ]

            injected_members: Sequence[Member] = []

            if self.attributes.injector:
                recur = True
                while null_members and recur:
                    recur = False
                    for member in null_members:
                        value, success = self.attributes.injector.try_inject_null_property(self.attributes.serializable, member)
                        if success:
                            null_members = [ null_member for null_member in null_members if null_member != member ]
                            data = { **data, ** { member.name: value }}
                            injected_members.append(member)
                            recur = True
                            break


            null_members = [
                member for member in null_members
                if not member.is_nullable
            ]

            if len(null_members) > 0:
                null_members_str = "', '".join([ member.name for member in null_members ])
                raise DeserializationException(f"Cannot deserialize type '{serialize_type(self.attributes.serializable)}' from data, because following non-nullable members are NULL: '{null_members_str}'", path)

            if self.attributes.strict:
                if len(data.keys()) != len(self.attributes.members):
                    raise DeserializationException(f"Cannot deserialize type '{serialize_type(self.attributes.serializable)}' from data, because serialized data contains more or less members than expected, and strategy is STRICT", path)

            deserialized = {
                member.name: data[member.name] if member in injected_members else self.__deserialize_member(member, data, f"{path}.{member.name}")
                for member in self.attributes.members
            }

            return cast(T, self.attributes.deserializer.deserialize(self.attributes.serializable, deserialized))


    def __deserialize_member(self, member: Member, data: PrimitiveMapping, path: str) -> Any:
        if member.name not in data:
            return None #dont throw any exceptions, since NULL values are not necessarily serialized

        return self.__deserialize_value(data[member.name], member.return_type, path)

    def __deserialize_value(self, value: Primitives, member_type: AnyType | None, path: str) -> Any:

        if isinstance(value, abc.Mapping) and TYPE_DESCRIPTOR in value:
            if VALUE_DESCRIPTOR in value:
                member_type, value = unwrap_value(cast(Mapping[str, Any], value))
            else:
                member_type, value = unwrap(cast(Mapping[str, Any], value))

        decoded, decode_result = self.__formatter.decode(value, member_type)
        if decode_result:
            value = decoded

        if member_type is not None:
            generic_origin: TypeParameter = get_generic_origin(member_type)
            generic_args = get_generic_arguments(member_type)

            if is_union(member_type):
                union_types = get_union_types(cast(UnionParameter, member_type))

                if isinstance_typing(value, union_types):
                    return value

                if is_primitive(value):
                    union_types = sorted(union_types, key = lambda t: isinstance_typing(value, t), reverse = True)

                for union_type in union_types:
                    try:
                        return self.__deserialize_value(value, union_type, path)
                    except: # noqa: E722
                        pass

            elif issubclass(generic_origin, tuple) and isinstance(value, list):
                return self.__deserialize_tuple(value, cast(TypeParameter, generic_origin), generic_args, member_type, path)
            elif issubclass(generic_origin, list) and isinstance(value, list):
                return self.__deserialize_list(value, cast(TypeParameter, generic_origin), generic_args, member_type, path)
            elif issubclass(generic_origin, set) and isinstance(value, (set, list)):
                return self.__deserialize_set(value, cast(TypeParameter, generic_origin), generic_args, member_type, path)
            elif issubclass(generic_origin, abc.Mapping) and isinstance(value, (dict, Mapping)):
                return self.__deserialize_dict(value, cast(TypeParameter, generic_origin), generic_args, member_type, path)
            elif isinstance(value, (dict, Mapping)):
                # if not self.attributes.strict and not is_serializable(member_type): # try to make serializable
                #     create_serializer(cast(type[Any], member_type), self.__formatter_type, deserializer=DefaultDeserializer, strict=self.attributes.strict, injector=self.attributes.injector)

                serializer = cast(BaseSerializer[type[Any]], BaseSerializer[member_type](self.__formatter_type))
                return serializer.__deserialize(value, path)

            elif isinstance_typing(value, member_type):
                return value

            raise DeserializationException(f"Unable to deserialize value '{value}' as type {get_type_name(member_type)}", path)
        elif is_primitive(value):
            return cast(Primitive, value)
        else:
            raise DeserializationException(f"Unable to deserialize value '{value}' due to missing type hints", path)

    def __deserialize_tuple(self, value: abc.Sequence[Any], generic_origin: TypeParameter, generic_args: TypeArgs, member_type: AnyType | None, path: str) -> tuple[Any, ...]:
        is_variadic = member_type and is_variadic_tuple_type(cast(type[tuple[Any, ...]], member_type))
        variadic_type = generic_args[0] if generic_args and is_variadic else None

        if not any(value):
            return tuple()
        elif generic_args and not is_variadic:
            deserialized_list: abc.Sequence[Any] = []
            for index, (generic_type, item) in enumerate(zip(generic_args, cast(tuple[Any], value))):
                try:
                    deserialized_list.append(self.__deserialize_value(item, generic_type, path))
                except DeserializationException as ex:
                    raise DeserializationException(ex.error, f"{path}[{index}]") from ex
            return tuple(deserialized_list)
        else:
            deserialized_list: abc.Sequence[Any] = []
            for index, item in enumerate(value):
                try:
                    deserialized_list.append(self.__deserialize_value(item, variadic_type, path))
                except DeserializationException as ex:
                    raise DeserializationException(ex.error, f"{path}[{index}]") from ex
            return tuple(deserialized_list)

    def __deserialize_list(self, value: abc.Sequence[Any], generic_origin: TypeParameter, generic_args: TypeArgs, member_type: AnyType | None, path: str) -> list[Any]:
        if generic_args:
            generic_type = generic_args[0]
            list_type: type[list[Any]] = construct_generic_type(generic_origin, generic_type)
            deserialized_list = list_type()
            for index, item in enumerate(value):
                try:
                    deserialized_list.append(self.__deserialize_value(item, generic_type, path))
                except DeserializationException as ex:
                    raise DeserializationException(ex.error, f"{path}[{index}]") from ex
            return deserialized_list
        else:
            deserialized_list: MutableSequence[Any] = []
            for index, item in enumerate(value):
                try:
                    deserialized_list.append(self.__deserialize_value(item, None, path))
                except DeserializationException as ex:
                    raise DeserializationException(ex.error, f"{path}[{index}]") from ex
            return deserialized_list

    def __deserialize_set(self, value: abc.Sequence[Any], generic_origin: TypeParameter, generic_args: TypeArgs, member_type: AnyType | None, path: str) -> set[Any]:
        if generic_args:
            generic_type = generic_args[0]
            set_type: type[set[Any]] = construct_generic_type(generic_origin, generic_type)
            deserialized_set = set_type()
            for index, item in enumerate(value):
                try:
                    deserialized_set.add(self.__deserialize_value(item, generic_type, path))
                except DeserializationException as ex:
                    raise DeserializationException(ex.error, f"{path}[{index}]") from ex
            return deserialized_set
        else:
            deserialized_set: set[Any] = set()
            for index, item in enumerate(value):
                try:
                    deserialized_set.add(self.__deserialize_value(item, None, path))
                except DeserializationException as ex:
                    raise DeserializationException(ex.error, f"{path}[{index}]") from ex
            return deserialized_set

    def __deserialize_dict(self, value: abc.Mapping[Any, Any], generic_origin: TypeParameter, generic_args: TypeArgs, member_type: AnyType | None, path: str) -> dict[Any, Any]:
        if generic_args:
            generic_key_type, generic_value_type = generic_args
            dict_type: type[dict[Any, Any]] = construct_generic_type(generic_origin, *[generic_key_type, generic_value_type])
            deserialized_dict = dict_type()
            for key, value in value.items():
                try:
                    deserialized_dict[self.__deserialize_value(key, generic_key_type, path)] = self.__deserialize_value(value, generic_value_type, path)
                except DeserializationException as ex:
                    raise DeserializationException(ex.error, f"{path}{{{key}}}") from ex
            return deserialized_dict
        else:
            deserialized_dict: dict[Any, Any] = {}
            for key, value in value.items():
                try:
                    deserialized_dict[self.__deserialize_value(key, None, path)] = self.__deserialize_value(value, None, path)
                except DeserializationException as ex:
                    raise DeserializationException(ex.error, f"{path}{{{key}}}") from ex
            return deserialized_dict

    @staticmethod
    def __get_serializer(serializable: type[T], formatter: type[Formatter]) -> BaseSerializer[T]:
        with BaseSerializer.__serializer_cache_lock__:
            key = (serializable, formatter)
            if key not in BaseSerializer.__serializer_cache__:
                BaseSerializer.__serializer_cache__[key] = BaseSerializer[serializable](formatter) # pragma: no cover
            return BaseSerializer.__serializer_cache__[key]


def serialize(
    obj: T,
    base: type[T] | None,
    formatter: type[Formatter], /,
) -> PrimitiveMapping:
    """Serializes the object to a basic dictionary

    Args:
        obj (T): The object to serialize
        formatter (Formatter): [description].
        generic_type (type[T]): The base type

    Returns:
        Mapping[str, Any]: A dictionary
    """
    if base:
        serializer = BaseSerializer[base](formatter)
        return serializer.serialize(obj, base = base)
    else:
        serializer = cast(BaseSerializer[T], BaseSerializer[type(obj)](formatter))
        return serializer.serialize(obj)

def deserialize(
    data: PrimitiveMapping,
    base: type[T] | None,
    formatter: type[Formatter], /
) -> T:
    if base:
        serializer = cast(BaseSerializer[T], BaseSerializer[base](formatter))
        return serializer.deserialize(data)
    else:
        cls, _ = unwrap(data)
        serializer = cast(BaseSerializer[T], BaseSerializer[cast(type[T], cls)](formatter))
        return serializer.deserialize(data)

def unwrap(data: PrimitiveMapping) -> tuple[AnyType, PrimitiveMapping]:
    if TYPE_DESCRIPTOR in data:
        type_descriptor = cast(str, data[TYPE_DESCRIPTOR])
        if type_descriptor in SERIALIZABLE_TYPE_DEFS:
            cls = SERIALIZABLE_TYPE_DEFS[type_descriptor]
            data = { key: value for key, value in data.items() if key != TYPE_DESCRIPTOR }
            return cls, data
        else:
            raise Exception(f"Type '{type_descriptor}' is not serializable") # pragma: no cover
    else:
        raise Exception("Unable to deserialize string without type information.") # pragma: no cover

def unwrap_value(data: PrimitiveMapping) -> tuple[AnyType, Primitive]:
    if TYPE_DESCRIPTOR in data and VALUE_DESCRIPTOR in data:
        type_descriptor = cast(str, data[TYPE_DESCRIPTOR])
        if type_descriptor in SERIALIZABLE_TYPE_DEFS:
            cls = SERIALIZABLE_TYPE_DEFS[type_descriptor]
            value = data[VALUE_DESCRIPTOR]
            return cls, cast(Primitive, value)
        else:
            raise Exception(f"Type '{type_descriptor}' is not serializable") # pragma: no cover
    else:
        raise Exception("Unable to deserialize string without type information.") # pragma: no cover

