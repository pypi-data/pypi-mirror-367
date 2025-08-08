from typing import TypeVar, Callable, overload
from typingutils import get_type_name

from runtime.serialization.core.threading import Lock

T = TypeVar('T')

SERIALIZABLE_DELEGATES: set[type] = set()
LOCK = Lock()

class SerializableDelegateDecorator:

    @overload
    def __call__(self) -> Callable[[type[T]], type[T]]:
        """Defines a delegate as serializable.
        """
        ...
    @overload
    def __call__(self, cls: type[T]) -> type[T]:
        """Defines a delegate as serializable.
        """
        ...
    def __call__(self, cls: type[T] | None = None) -> Callable[[type[T]], type[T]] | type[T]:
        def decorate(cls: type[T]) -> type[T]:
            with LOCK:
                if cls in SERIALIZABLE_DELEGATES:
                    raise Exception(f"Class '{get_type_name(cls)}' is already a registered as a serializable delegate") # pragma: no cover
                else:
                    SERIALIZABLE_DELEGATES.add(cls)
                return cls

        if cls:
            return decorate(cls)
        else:
            return decorate # pragma: no cover

serializable_delegate = SerializableDelegateDecorator()

