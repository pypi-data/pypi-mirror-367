from abc import ABC, abstractmethod
from typing import Any

from runtime.serialization.core.member import Member

class Injector(ABC):
    """The Injector class is intended for injecting values into objects when they are null.
    """

    @abstractmethod
    def try_inject_null_property(self, obj_type: type, member: Member) -> tuple[Any | None, bool]:
        return None, False