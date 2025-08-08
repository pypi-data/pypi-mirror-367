from typing import Any, Callable

from runtime.serialization.core.threading import Lock

RESOLVABLE_TYPES: set[type] = set()
REGISTRATIONS: dict[type, list[tuple[Callable[[Any], bool], type]]] = {}
LOCK = Lock()
