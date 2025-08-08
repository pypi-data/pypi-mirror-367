from typing import Protocol, runtime_checkable
from abc import abstractmethod

@runtime_checkable
class SupportsBool(Protocol):
    __slots__ = ()

    @abstractmethod
    def __bool__(self) -> bool:
        pass
