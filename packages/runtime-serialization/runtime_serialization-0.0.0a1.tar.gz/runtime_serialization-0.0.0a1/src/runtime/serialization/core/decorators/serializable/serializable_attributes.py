from __future__ import annotations
from typing import TypeVar

from runtime.serialization.core.serializer_attributes import SERIALIZABLE_LOCK, SERIALIZABLES
from runtime.serialization.core.interfaces.deserializer import Deserializer
from runtime.serialization.core.interfaces.injector import Injector
from runtime.serialization.core.decorators.decorator_exception import DecoratorException

T = TypeVar("T")

SERIALIZABLE_ATTRIBUTES: dict[type, SerializableAttributes] = {}

class SerializableAttributes:
    __slots__ = [ "__namespace", "__strict", "__deserializer", "__type_finder", "__injector" ]

    def __init__(
        self, *,
        namespace: str | None = None,
        strict: bool | None = None,
        deserializer: type[Deserializer] | None = None,
        injector: type[Injector] | None = None
    ):
        self.__namespace = namespace
        self.__strict = strict
        self.__deserializer = deserializer
        self.__injector = injector

    @property
    def namespace(self) -> str | None:
        return self.__namespace

    @namespace.setter
    def namespace(self, value: str):
        if not self.__namespace is None:
            raise DecoratorException("Namespace attribute is already specified") # pragma: no cover
        self.__namespace = value

    @property
    def strict(self) -> bool | None:
        return self.__strict

    @strict.setter
    def strict(self, value: bool):
        if not self.__strict is None:
            raise DecoratorException("Strict attribute is already specified") # pragma: no cover
        self.__strict = value

    @property
    def deserializer(self) -> type[Deserializer] | None:
        return self.__deserializer

    @deserializer.setter
    def deserializer(self, value: type[Deserializer]):
        if not self.__deserializer is None:
            raise DecoratorException("Deserializer attribute is already specified") # pragma: no cover
        self.__deserializer = value

    @property
    def injector(self) -> type[Injector] | None:
        return self.__injector

    @injector.setter
    def injector(self, value: type[Injector]):
        if not self.__injector is None:
            raise DecoratorException("Injector attribute is already specified") # pragma: no cover
        self.__injector = value


def get_or_set_attributes(
    cls: type, *,
    namespace: str | None = None,
    strict: bool | None = None,
    deserializer: type[Deserializer] | None = None,
    injector: type[Injector] | None = None
) -> SerializableAttributes:
    with SERIALIZABLE_LOCK:
        if not cls in SERIALIZABLES:
            if not cls in SERIALIZABLE_ATTRIBUTES:
                attributes = SerializableAttributes(
                    namespace = namespace,
                    strict = strict,
                    deserializer = deserializer,
                    injector = injector
                )
                SERIALIZABLE_ATTRIBUTES[cls] = attributes
            else:
                attributes = SERIALIZABLE_ATTRIBUTES[cls]
                if namespace is not None:
                    attributes.namespace = namespace
                if strict is not None:
                    attributes.strict = strict
                if deserializer is not None:
                    attributes.deserializer = deserializer
                if injector is not None:
                    attributes.injector = injector

            return attributes
        else:
            raise DecoratorException("Serializable decorator can only be applied once")

def remove_attributes(cls: type) -> None:
    with SERIALIZABLE_LOCK:
        if cls in SERIALIZABLE_ATTRIBUTES:
            del SERIALIZABLE_ATTRIBUTES[cls]
        else:
            pass # pragma: no cover