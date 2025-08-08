from typing import TypeVar, Any, IO, overload, cast
from io import TextIOBase
from os import path
from yaml import load as load_data, dump as dump_data, SafeLoader

from runtime.serialization.core.base_serializer import BaseSerializer, deserialize as deserialize_base
from runtime.serialization.core.formats.yaml.formatter import Formatter
from runtime.serialization.core.interfaces.serializer import Serializer

T = TypeVar('T')

class YamlSerializer(Serializer[T]):
    __slots__ = ["__base"]

    def __new__(cls, *args: Any, **kwargs: Any):
        return cast(YamlSerializer[T], super().__new__(cls, *args, **kwargs))

    def __init__(self):
        self.__base = BaseSerializer[self.serializable](Formatter)


    @overload
    def serialize(self, obj: T) -> str:
        """Serializes the object to a YAML string

        Args:
            obj (T): The object to serialize

        Returns:
            str: A YAML string
        """
        ...
    @overload
    def serialize(self, obj: T, base: type[Any]) -> str:
        """Serializes the object to a YAML string

        Args:
            obj (T): The object to serialize
            base (type[Any]): The base type

        Returns:
            str: A YAML string
        """
        ...
    def serialize(self, obj: T, base: type[Any] | None = None) -> str:
        if base:
            data = self.__base.serialize(obj, base = base)
        else:
            data = self.__base.serialize(obj, base = self.__base.attributes.serializable)

        return dump_data(data, default_flow_style=False, sort_keys=True)

    @overload
    def dump(self, obj: T, output: TextIOBase | IO[Any], **kwargs: Any) -> None:
        ...
    @overload
    def dump(self, obj: T, output: str, *, overwrite: bool = False, **kwargs: Any) -> None:
        ...
    def dump(self, obj: T, output: TextIOBase | IO[Any] | str, *, overwrite: bool = False, **kwargs: Any) -> None:
        if isinstance(output, str):
            if path.isfile(output) and not overwrite:
                raise FileExistsError
            elif not path.isfile(output):
                with open(output, "a"): # ensure that file exists
                    pass
            with open(output, "wt", encoding = "utf-8") as file:
                serialized = self.serialize(obj)
                file.write(serialized)
        else:
            serialized = self.serialize(obj)
            output.write(serialized)

    def dumps(self, obj: T, *, pretty_print: bool = True) -> str:
        return self.serialize(obj)

    def deserialize(self, text: str) -> T:
        """Deserializes a YAML string to an object

        Args:
            text (str): The YAML string to deserialize

        Returns:
            T: An object
        """
        data = load_data(text, SafeLoader)
        return self.__base.deserialize(data)

    @overload
    def load(self, input: TextIOBase | IO[Any]) -> T:
        ...
    @overload
    def load(self, input: str) -> T:
        ...
    def load(self, input: TextIOBase | IO[Any] | str) -> T:
        if isinstance(input, str):
            if not path.isfile(input):
                raise FileNotFoundError # pragma: no cover
            with open(input, "rt", encoding = "utf-8") as file:
                text = file.read()
                return self.deserialize(text)
        else:
            text = input.read()
            return self.deserialize(text)

    def loads(self, text: str) -> T:
        return self.deserialize(text)



@overload
def serialize(obj: object) -> str:
    """Serializes the object to a YAML string

    Args:
        obj (object): The object to serialize

    Returns:
        str: YAML string
    """
    ...
@overload
def serialize(obj: T, base: type[T]) -> str:
    """Serializes the object to a YAML string, using the Serializer of a specific base class.
    This is useful when serializing an object, where only the base type is serializable.

    Args:
        obj (T): The object to serialize
        base (type[T]): The base class

    Returns:
        str: A YAML string
    """
    ...
def serialize(obj: T, base: type[T] | None = None) -> str:
    if base:
        serializer = YamlSerializer[base]()
        return serializer.serialize(obj, base)
    else:
        serializer = YamlSerializer[type(obj)]()
        return serializer.serialize(obj, cast(type[T], object))


@overload
def deserialize(text: str) -> Any:
    """Deserializes a YAML string to an object

    Args:
        text (str): The YAML string to deserialize

    Returns:
        T: The deserialized object
    """
    ...
@overload
def deserialize(text: str, base: type[T]) -> T:
    """Deserializes a YAML string to an object of the specified type

    Args:
        text (str): The YAML string to deserialize
        base (type[T]): The type of serializable to deserialize into

    Returns:
        T: The deserialized object
    """
    ...
def deserialize(text: str, base: type[T] | None = None) -> T | Any:
    if base:
        serializer = YamlSerializer[base]()
        return serializer.deserialize(text)
    else:
        data = load_data(text, SafeLoader)
        return deserialize_base(data, None, Formatter)
