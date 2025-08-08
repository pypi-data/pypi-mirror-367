from typing import TypeVar, Sequence, Mapping, Any
from abc import ABC, abstractmethod

from runtime.serialization.core.member import Member

T = TypeVar('T')

class Deserializer(ABC):
    __slots__ = []

    def __init__(self, cls: type, members: Sequence[Member], strict: bool):
        pass

    @abstractmethod
    def deserialize(self, cls: type[T], data: Mapping[str, Any]) -> T:
        pass