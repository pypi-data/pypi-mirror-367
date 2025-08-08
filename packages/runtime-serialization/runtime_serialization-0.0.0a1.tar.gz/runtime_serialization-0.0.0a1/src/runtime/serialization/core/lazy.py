from __future__ import annotations
from typing import Callable, TypeVar, Generic, cast

from runtime.serialization.core.threading import Lock

T = TypeVar("T")

class Lazy(Generic[T]):
    __slots__ = ["__lock", "__fn_resolve", "__fn_additional", "__resolved"]

    def __init__(self, fn_resolve: Callable[[], T]) -> None:
        self.__lock = Lock()
        self.__fn_resolve: Callable[[], T] | None = fn_resolve
        self.__fn_additional: list[Callable[[], None]] = []
        self.__resolved: T | None = None

    def __add__(self, fn: Callable[[], None]) -> Lazy[T]:
        """Add additional callback to be invoked after resolve.

        Args:
            fn (Callable[[], None]): The callback function
        """
        self.__fn_additional.append(fn)
        return self

    def __call__(self) -> T:
        return self.__get__()

    def __get__(self) -> T:
        with self.__lock:
            if not self.__resolved:
                self.__resolved = cast(Callable[[], T], self.__fn_resolve)()
                self.__fn_resolve = None

                for fn in self.__fn_additional:
                    fn()

                self.__fn_additional.clear()

        return self.__resolved
