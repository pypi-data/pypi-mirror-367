from typing import Any, cast

class DictObject:
    __slots__ = ["__data"]
    def __init__(self, data: dict[str, Any]):
        self.__data = data

    def __getattribute__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_DictObject__data") # if accessing `self.__data` a recursion will happen
        if name in data:
            data = data[name]
            return DictObject(cast(dict[str, Any], data)) if isinstance(data, dict) else data
        else:
            return super().__getattribute__(name) # pragma: no cover
