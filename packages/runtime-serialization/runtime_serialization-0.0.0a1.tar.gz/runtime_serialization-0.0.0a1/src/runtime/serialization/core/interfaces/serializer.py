from __future__ import annotations
from typing import Any, IO, TypeVar, Generic, cast, overload
from io import TextIOBase
from abc import ABC, abstractmethod
from typingutils import AnyType, get_generic_arguments

from runtime.serialization.core.threading import Lock

T = TypeVar("T")

class Serializer(Generic[T], ABC):
    __serializer_cache_lock__ = Lock()
    __serializer_cache__: dict[tuple[type[Any], AnyType], Serializer[Any]] = {}
    __serializable: type[Any]

    def __new__(cls, *args: Any, **kwargs: Any):
        serializable, *_ = get_generic_arguments(cls)
        key = (cls, serializable)
        with Serializer.__serializer_cache_lock__:
            if not key in Serializer.__serializer_cache__:
                instance = object.__new__(cls)
                instance.__serializable = cast(type[Any], serializable)
                Serializer.__serializer_cache__[key] = instance
                return instance
            else:
                return Serializer.__serializer_cache__[key]

    @property
    def serializable(self) -> type[Any]:
        return self.__serializable


    @overload
    @abstractmethod
    def serialize(self, obj: T) -> str:
        ...
    @overload
    @abstractmethod
    def serialize(self, obj: T, base: type[T]) -> str:
        ...

    @abstractmethod
    def deserialize(self, text: str) -> T:
        ...

    @overload
    @abstractmethod
    def load(self, input: TextIOBase | IO[Any]) -> T:
        ...
    @overload
    @abstractmethod
    def load(self, input: str) -> T:
        ...

    @abstractmethod
    def loads(self, text: str) -> T:
        ...

    @overload
    @abstractmethod
    def dump(self, obj: T, output: TextIOBase | IO[Any], **kwargs: Any) -> None:
        ...
    @overload
    @abstractmethod
    def dump(self, obj: T, output: str, *, overwrite: bool = False, **kwargs: Any) -> None:
        ...

    @abstractmethod
    def dumps(self, obj: T) -> str:
        ...