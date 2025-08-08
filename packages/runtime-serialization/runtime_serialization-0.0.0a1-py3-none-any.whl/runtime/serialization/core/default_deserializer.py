from typing import TypeVar, Sequence, Mapping, Any, cast
from typingutils import get_optional_type, issubclass_typing, is_generic_type, get_type_name
from typingutils.internal import get_generic_origin
from runtime.reflection.lite import Parameter, ParameterKind, get_constructor

from runtime.serialization.core.not_serializable_exception import NotSerializableException
from runtime.serialization.core.deserialization_strategy import DeserializationStrategy
from runtime.serialization.core.member import Member
from runtime.serialization.core.member_type import MemberType
from runtime.serialization.core.interfaces.deserializer import Deserializer


T = TypeVar('T')

BUILTIN_GENERIC_TYPES = (tuple, list, dict, set)

class DefaultDeserializer(Deserializer):
    """
    The default deserializer.
    """

    __slots__ = ["__strategy", "__members", "__strict", "__ctor_pos_args"]

    def __init__(self, cls: type, members: Sequence[Member], strict: bool):
        self.__members = members
        self.__ctor_pos_args: Sequence[str] = []
        origin = get_generic_origin(cls)
        sig = get_constructor(origin)
        args: Sequence[Parameter] = [ arg for arg in sig.parameters if arg.kind not in (ParameterKind.ARGS, ParameterKind.KWARGS) ]

        pos_args = [ arg for arg in args if arg.kind == ParameterKind.POSITIONAL_OR_KEYWORD ]
        pos_args_names = set([ arg.name for arg in pos_args ])
        members_names = set([ member.name for member in members ])

        empty_constructor = not args

        if pos_args_names == members_names:
            # class instantiation via constructor
            for member in members:
                arg = [ a for a in pos_args if a.name == member.name ][0]
                arg_type, arg_nullable = get_optional_type(cast(type, arg.parameter_type))
                if not strict and not arg_type:
                    arg_type = type[Any]

                if isinstance(arg_type, TypeVar) and arg_type is member.return_type:
                    pass
                elif not strict and not member.return_type:
                    pass
                elif not member.return_type: # pragma: no cover - will be caught in the serializer
                    raise NotSerializableException(cls, f"Deserializer cannot deserialize type because member '{member.name}' is not annotated which is not allowed in strict mode")
                elif not issubclass_typing(arg_type, member.return_type) or arg_nullable != member.is_nullable:
                    raise NotSerializableException(cls, f"Deserializer cannot deserialize type because type of argument '{arg.name}' doesn't match the member type '{get_type_name(member.return_type)}'")
                elif strict and (is_generic_type(member.return_type) or member.return_type in BUILTIN_GENERIC_TYPES):
                    raise NotSerializableException(cls, f"Deserializer cannot deserialize type because type of member '{member.name}' is a non-subscripted generic type which is not allowed in strict mode")

            self.__ctor_pos_args = [
                arg for arg, _ in sorted(
                    {
                        value.name: pos_args.index(value)
                        for value in pos_args
                    }.items(),
                    key = lambda a: a[1]
                )
            ]

            self.__strategy = DeserializationStrategy.CONSTRUCTOR
        elif empty_constructor and not any([ member for member in members if member.member_type != MemberType.FIELD ]):
            # class instantiation via individual fields
            self.__strategy = DeserializationStrategy.FIELDS
        elif empty_constructor and not any([ member for member in members if member.member_type != MemberType.FIELD and member.is_readonly ]):
            # class instantiation via individual fields and/or property setters
            self.__strategy = DeserializationStrategy.FIELDS_OR_PROPERTIES
        else:
            raise NotSerializableException(cls, "DefaultDeserializer cannot deserialize type")


    def deserialize(self, cls: type[T], data: Mapping[str, Any]) -> T:
        if self.__strategy == DeserializationStrategy.CONSTRUCTOR:
            # reorganize arguments, to match constructor's arrangement
            return cls(*[ data[arg] for arg in self.__ctor_pos_args ])
        elif self.__strategy in (DeserializationStrategy.FIELDS, DeserializationStrategy.FIELDS_OR_PROPERTIES):
            obj = cls()
            for member in self.__members:
                member.set_value(obj, data[member.name])
            return obj
        else:
            raise NotImplementedError(f"Cannot deserialize type '{get_type_name(cls)}' due to unsupported strategy '{self.__strategy.name}'") # pragma: no cover
