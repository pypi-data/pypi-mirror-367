from typing import TypeVar, Callable, overload
from typingutils import get_type_name

from runtime.serialization.core.decorators.type_resolving.registry import RESOLVABLE_TYPES, LOCK
from runtime.serialization.core.decorators.decorator_exception import DecoratorException

T = TypeVar('T')

class ResolvableDecorator:
    @overload
    def __call__(self) -> Callable[[type[T]], type[T]]:
        """Defines a base class as resolvable. Further implementation requires that all derived classes are
        decorated with the @resolve decorator, and are imported at resolve time.
        """
        ...
    @overload
    def __call__(self, cls: type[T]) -> type[T]:
        """Defines a base class as resolvable. Further implementation requires that all derived classes are
        decorated with the @resolve decorator, and are imported at resolve time.
        """
        ...
    def __call__(self, cls: type[T] | None = None) -> Callable[[type[T]], type[T]] | type[T]:
        def decorate(cls: type[T]) -> type[T]:
            with LOCK:
                if cls in RESOLVABLE_TYPES:
                    raise DecoratorException(f"Base class '{get_type_name(cls)}' is already a registered resolvable")
                else:
                    RESOLVABLE_TYPES.add(cls)
                return cls

        if cls:
            return decorate(cls)
        else:
            return decorate

resolvable = ResolvableDecorator()

def is_resolvable(cls: type) -> bool:
    """Indicates whether or not type can be resolved to derived types.

    Args:
        cls (type): The base class
    """
    return cls in RESOLVABLE_TYPES
