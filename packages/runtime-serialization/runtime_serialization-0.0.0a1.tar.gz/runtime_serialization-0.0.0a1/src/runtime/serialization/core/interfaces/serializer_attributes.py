from abc import ABC, abstractmethod

from runtime.serialization.core.member import Member
from runtime.serialization.core.interfaces.deserializer import Deserializer
from runtime.serialization.core.interfaces.injector import Injector


class SerializerAttributes(ABC):

    @property
    @abstractmethod
    def serializable(self) -> type:
        ...

    @property
    @abstractmethod
    def namespace(self) -> str | None:
        ...

    @property
    @abstractmethod
    def type_name(self) -> str:
        ...

    @property
    @abstractmethod
    def strict(self) -> bool:
        ...

    @property
    @abstractmethod
    def deserializer(self) -> Deserializer:
        ...

    @property
    @abstractmethod
    def is_resolvable(self) -> bool:
        ...

    @property
    @abstractmethod
    def injector(self) -> Injector | None:
        ...

    @property
    @abstractmethod
    def members(self) -> tuple[Member, ...]:
        ...