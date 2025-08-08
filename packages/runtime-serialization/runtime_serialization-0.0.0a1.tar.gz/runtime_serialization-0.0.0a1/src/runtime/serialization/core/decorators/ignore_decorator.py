from typing import TypeVar, Any, Callable, overload

from runtime.serialization.core.threading import Lock
from runtime.serialization.core.decorators.decorator_exception import DecoratorException

T = TypeVar("T")

IGNORED: list[Any] = []
LOCK = Lock()

class IgnoreDecorator:

    @overload
    def __call__(self) -> Callable[[T], T]:
        """Makes the member non-serializable
        """
        ...
    @overload
    def __call__(self, member: T) -> T:
        """Makes the member non-serializable
        """
        ...
    def __call__(self, member: T | None = None) -> Callable[[T], T] | T:
        def decorate(member: T) -> T:
            with LOCK:
                if member in IGNORED:
                    raise DecoratorException(f"Class member '{member}' is already a registered as ignored") # pragma: no cover
                else:
                    IGNORED.append(member)
                return member

        if member:
            return decorate(member)
        else:
            return decorate

ignore = IgnoreDecorator()
