from __future__ import annotations
from typing import TypeVar, overload, cast
from typingutils import AnyType, get_generic_parameters, get_generic_arguments, issubclass_typing, is_generic_type, get_type_name

from runtime.serialization.core.lazy import Lazy
from runtime.serialization.core.helpers import get_members
from runtime.serialization.core.not_serializable_exception import NotSerializableException
from runtime.serialization.core.member import Member
from runtime.serialization.core.interfaces.deserializer import Deserializer
from runtime.serialization.core.decorators.type_resolving.resolvable_decorator import is_resolvable
from runtime.serialization.core.decorators.decorator_exception import DecoratorException
from runtime.serialization.core.default_deserializer import DefaultDeserializer
from runtime.serialization.core.interfaces.injector import Injector
from runtime.serialization.core.shared import serialize_type
from runtime.serialization.core.serializer_attributes_registry import SERIALIZABLE_LOCK, SERIALIZABLE_TYPE_DEFS, SERIALIZABLE_TYPE_GENERIC_PARAMETERS, SERIALIZABLES
from runtime.serialization.core.interfaces.serializer_attributes import SerializerAttributes as SerializerAttributesInterface

T = TypeVar("T")

class SerializerAttributes(SerializerAttributesInterface):
    __slots__ = ["__ns", "__type_name", "__deserializer", "__resolvable", "__members", "__generic_type", "__strict", "__injector"]

    def __init__(
        self,
        serializable: type,
        namespace: str | None,
        type_name: str,
        deserializer: type[Deserializer],
        injector: type[Injector] | None,
        strict: bool = False
    ):
        self.__generic_type = serializable
        self.__ns = namespace
        self.__type_name = type_name
        self.__strict = strict
        self.__members = get_members(self.__generic_type, strict)


        for member in self.__members:
            if strict and not member.return_type:
                raise NotSerializableException(serializable, f"Member '{get_type_name(serializable)}.{member.name}' is not annotated/typed")

            if strict or member.return_type and [
                True
                for serializable_type, generic in SERIALIZABLE_TYPE_GENERIC_PARAMETERS.items()
                if generic and (
                    not isinstance(member.return_type, TypeVar)
                    and issubclass_typing(member.return_type, serializable_type)
                )
            ]:
                from runtime.serialization.core.shared import check_serializable
                check_serializable(cast(AnyType, member.return_type))


        self.__deserializer = deserializer(self.__generic_type, self.__members, strict)
        self.__resolvable = is_resolvable(serializable)
        self.__injector = injector() if injector else None



    @property
    def serializable(self) -> type:
        return self.__generic_type

    @property
    def namespace(self) -> str | None:
        return self.__ns

    @property
    def type_name(self) -> str:
        return self.__type_name

    @property
    def strict(self) -> bool:
        return self.__strict

    @property
    def deserializer(self) -> Deserializer:
        return self.__deserializer

    @property
    def is_resolvable(self) -> bool:
        return self.__resolvable

    @property
    def injector(self) -> Injector | None:
        return self.__injector

    @property
    def members(self) -> tuple[Member, ...]:
        return self.__members

    @staticmethod
    def create(
        serializable: type, /,
        namespace: str | None = None,
        deserializer: type[Deserializer] = DefaultDeserializer,
        injector: type[Injector] | None = None,
        strict: bool = False
    ) -> Lazy[SerializerAttributes]:
        """Makes object serializable, and returns the serializer.
        Use @serializable decorator instead of calling this method directly.

        Args:
            serializable (type): The type
            namespace (str | None). The namespace of the class.
            deserializer (type[Deserializer]): The deserializer type. Defaults to DefaultDeserializer.
            injector (type[Injector] | None): The member Injector type. Defaults to None.
            strict (bool, optional): The strictness. Defaults to False.

        Returns:
            Lazy[SerializerAttributes]: A Serializer instance
        """
        if is_generic_type(serializable):
            raise NotSerializableException(serializable, "Serializable attributes are incompatible with non-subscripted generic types")

        if serializable not in SERIALIZABLES:
            if namespace:
                type_name = f"{namespace}.{serializable.__name__}"
            else:
                type_name = serialize_type(serializable).strip("'\"")

            with SERIALIZABLE_LOCK:
                generic_parameters = generic_arguments = 0
                if ( generic_parameters := len(get_generic_parameters(serializable)) ) or ( generic_arguments := len(get_generic_arguments(serializable)) ):
                    SERIALIZABLE_TYPE_GENERIC_PARAMETERS[serializable] = max(generic_parameters, generic_arguments)
                SERIALIZABLE_TYPE_DEFS[type_name] = serializable

                def lazy_fn() -> SerializerAttributes:
                    try:
                        return SerializerAttributes(
                            serializable,
                            namespace,
                            type_name,
                            deserializer,
                            injector,
                            strict
                        )
                    except NotSerializableException:
                        with SERIALIZABLE_LOCK:
                            if serializable in SERIALIZABLE_TYPE_GENERIC_PARAMETERS:
                                del SERIALIZABLE_TYPE_GENERIC_PARAMETERS[serializable] # pragma: no cover
                            if type_name in SERIALIZABLE_TYPE_DEFS:
                                del SERIALIZABLE_TYPE_DEFS[type_name] # pragma: no cover
                            if serializable in SERIALIZABLES:
                                del SERIALIZABLES[serializable] # pragma: no cover
                        raise

                SERIALIZABLES[serializable] = cast(Lazy[SerializerAttributesInterface], Lazy[SerializerAttributes](lazy_fn))

        return cast(Lazy[SerializerAttributes], SERIALIZABLES[serializable])



    @staticmethod
    def get(serializable: AnyType) -> SerializerAttributesInterface:
        """Gets the root serializer for the specific serializable type

        Args:
            serializable (type): The serializable type

        Raises:
            NotSerializableException: If type is not serializable

        Returns:
            SerializerAttributesProtocol: The serializer attributes
        """
        with SERIALIZABLE_LOCK:
            if serializable not in SERIALIZABLES:
                raise NotSerializableException(serializable)

            return SERIALIZABLES[serializable]()


    @overload
    @staticmethod
    def make_serializable(serializable: type, /) -> None:
        """Makes the class serializable
        """
        ...
    @overload
    @staticmethod
    def make_serializable(
        serializable: type, /,
        namespace: str | None = None,
        strict: bool = False,
        deserializer: type[Deserializer]=DefaultDeserializer
    ) -> None:
        """Makes the class serializable

        Args:
            namespace (str | None, optional): The class namespace. Defaults to None.
            strict (SerializationStrategy, optional): The strictness. Defaults to False.
            deserializer (type[Deserializer], optional): The deserializer. Defaults to DefaultDeserializer.

        """
        ...
    @overload
    @staticmethod
    def make_serializable(
        serializable: type, /,
        namespace: str | None = None,
        strict: bool = False,
        deserializer: type[Deserializer] = DefaultDeserializer,
        injector: type[Injector] | None = None
    ) -> None:
        """Makes the class serializable

        Args:
            namespace (str | None, optional): The class namespace. Defaults to None.
            strict (SerializationStrategy, optional): The strictness. Defaults to False.
            deserializer (type[Deserializer], optional): The deserializer. Defaults to DefaultDeserializer.
            injector (type[Injector], optional): The member Injector type. Defaults to None.

        """
        ...
    @staticmethod
    def make_serializable(
        serializable: type[T], /,
        namespace: str | None = None,
        strict: bool | None = False,
        deserializer: type[Deserializer] | None = None,
        injector: type[Injector] | None = None
    ) -> None:
        SerializerAttributes.make_serializable_lazy(
            serializable,
            namespace = namespace,
            strict = strict,
            deserializer = deserializer,
            injector = injector
        )()

    @staticmethod
    def make_serializable_lazy(
        serializable: type[T], /,
        namespace: str | None = None,
        strict: bool | None = None,
        deserializer: type[Deserializer] | None = None,
        injector: type[Injector] | None = None
    ) -> Lazy[SerializerAttributes]:

        with SERIALIZABLE_LOCK:
            if serializable not in SERIALIZABLES:
                from runtime.serialization.core.decorators.serializable.serializable_attributes import get_or_set_attributes, remove_attributes
                attributes = get_or_set_attributes(serializable)
                lazy = SerializerAttributes.create(
                    serializable,
                    namespace = namespace or attributes.namespace,
                    deserializer = deserializer or attributes.deserializer or DefaultDeserializer,
                    injector = injector or attributes.injector,
                    strict = strict or attributes.strict or False
                )
                def callback() -> None:
                    remove_attributes(serializable)

                lazy += callback
                return lazy
            else:
                raise DecoratorException("Serializable decorator can only be applied once")


