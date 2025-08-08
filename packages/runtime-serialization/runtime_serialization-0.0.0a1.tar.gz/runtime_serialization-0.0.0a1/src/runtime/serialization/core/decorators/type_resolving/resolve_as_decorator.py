from typing import TypeVar, Any, Callable, cast
from typingutils import get_type_name

from runtime.serialization.core.decorators.type_resolving.registry import RESOLVABLE_TYPES, REGISTRATIONS, LOCK
from runtime.serialization.core.decorators.decorator_exception import DecoratorException

T = TypeVar('T')
Tresolve = TypeVar('Tresolve')

class ResolveAsDecorator:
    def __call__(self, base: type[Tresolve], fn_resolve: Callable[[Tresolve], bool], /) -> Callable[[type[T]], type[T]]:
        """Adds a resolving function to the chain of base class resolvers. Further implementation requires that
        base class is decorated with the @resolvable decorator
        """
        def decorate(cls: type[T]) -> type[T]:
            with LOCK:
                if not issubclass(cls, base):
                    raise DecoratorException(f"Class '{get_type_name(cls)}' is not derived from '{get_type_name(base)}'")
                if not base in REGISTRATIONS:
                    derived: list[tuple[Callable[[Any], bool], type]] = []
                    REGISTRATIONS[base] = derived
                else:
                    derived = REGISTRATIONS[base]

                if [ resolved for _, resolved in derived if resolved is cls ]:
                    raise DecoratorException(f"Derived class '{get_type_name(cls)}' is already defined in resolve chain")

                derived.append((fn_resolve, cls))
                return cast(type[T], cls)
        return decorate


resolve_as = ResolveAsDecorator()

def resolve(base: type[T], data: T) -> type[T]:
    """Resolves a base class to a derived class.

    Args:
        base (type[T]): The base class.
        data (T): The base instance.

    Returns:
        type[T]: The derived type.
    """''
    if not base in RESOLVABLE_TYPES:
        raise Exception(f"Base class '{get_type_name(base)}' is not defined resolvable")

    result = [
        resolved
        for fn, resolved in REGISTRATIONS[base]
        if fn(data)
    ]
    if result and len(result) == 1:
        return cast(type[T], result[0])
    else:
        raise Exception("Unable to resolve")
