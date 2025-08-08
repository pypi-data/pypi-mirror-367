class DeserializationException(Exception):
    __slots__ = [ "__path", "__error" ]

    def __init__(self, error: str, path: str):
        super().__init__(f"Unable to deserialize member '{path}': {error}")
        self.__path = path
        self.__error = error

    @property
    def path(self) -> str | None:
        return self.__path

    @property
    def error(self) -> str:
        return self.__error

