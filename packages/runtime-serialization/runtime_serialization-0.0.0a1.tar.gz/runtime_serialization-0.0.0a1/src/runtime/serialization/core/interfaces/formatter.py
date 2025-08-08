from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod
from typingutils import AnyType

from runtime.serialization.core.threading import Lock
from runtime.serialization.core.helpers import Result
from runtime.serialization.core.primitives import Primitives

class Formatter(ABC):
    __formatter_cache_lock__ = Lock()
    __formatter_cache__: dict[type[Any], Formatter] = {}

    def __new__(cls, *args: Any, **kwargs: Any):
        with Formatter.__formatter_cache_lock__:
            if not cls in Formatter.__formatter_cache__:
                instance = object.__new__(cls)
                Formatter.__formatter_cache__[cls] = instance
                return instance
            else:
                return Formatter.__formatter_cache__[cls]

    @abstractmethod
    def encode(self, value: Any, member_type: AnyType | None) -> Result[Primitives]:
        ...

    @abstractmethod
    def decode(self, value: Primitives, member_type: AnyType | None) -> Result[Any]:
        ...
