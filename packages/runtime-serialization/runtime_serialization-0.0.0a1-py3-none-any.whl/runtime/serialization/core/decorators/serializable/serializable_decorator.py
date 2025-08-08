from typing import TypeVar, Callable, overload

from runtime.serialization.core.decorators.serializable.serializable_attributes import get_or_set_attributes
from runtime.serialization.core.serializer_attributes import SerializerAttributes
from runtime.serialization.core.interfaces.deserializer import Deserializer
from runtime.serialization.core.default_deserializer import DefaultDeserializer
from runtime.serialization.core.interfaces.injector import Injector

T = TypeVar('T')

class SerializableDecorator:

    @staticmethod
    def namespace(value: str) -> Callable[[type[T]], type[T]]:
        """Sets the deferred serializable attribute 'namespace'

        Args:
            value (str): The value
        """
        def decorate(cls: type[T]) -> type[T]:
            get_or_set_attributes(cls, namespace = value)
            return cls
        return decorate

    @staticmethod
    def strict(value: bool) -> Callable[[type[T]], type[T]]:
        """Sets the deferred serializable attribute 'strict'

        Args:
            value (str): The value
        """
        def decorate(cls: type[T]) -> type[T]:
            get_or_set_attributes(cls, strict = value)
            return cls
        return decorate

    @staticmethod
    def deserializer(value: type[Deserializer]) -> Callable[[type[T]], type[T]]:
        """Sets the deferred serializable attribute 'deserializer'

        Args:
            value (str): The value
        """
        def decorate(cls: type[T]) -> type[T]:
            get_or_set_attributes(cls, deserializer = value)
            return cls
        return decorate

    @staticmethod
    def injector(value: type[Injector]) -> Callable[[type[T]], type[T]]:
        """Sets the deferred serializable attribute 'injector'

        Args:
            value (str): The value
        """
        def decorate(cls: type[T]) -> type[T]:
            get_or_set_attributes(cls, injector = value)
            return cls
        return decorate

    @overload
    def __call__(self, cls: type[T], /) -> type[T]:
        """Makes the class serializable
        """
        ...
    @overload
    def __call__(
        self, *,
        namespace: str | None = None,
        strict: bool = False,
        deserializer: type[Deserializer]=DefaultDeserializer,
    ) -> Callable[[type[T]], type[T]]:
        """Makes the class serializable

        Args:
            namespace (str | None, optional): The class namespace. Defaults to None.
            strict (bool, optional): The strictness. Defaults to False.
            deserializer (type[Deserializer], optional): The deserializer. Defaults to DefaultDeserializer.
        """
        ...
    @overload
    def __call__(
        self, *,
        namespace: str | None = None,
        strict: bool = False,
        deserializer: type[Deserializer]=DefaultDeserializer,
        injector: type[Injector]
    ) -> Callable[[type[T]], type[T]]:
        """Makes the class serializable

        Args:
            namespace (str | None, optional): The class namespace. Defaults to None.
            strict (bool, optional): The strictness. Defaults to False.
            deserializer (type[Deserializer], optional): The deserializer. Defaults to DefaultDeserializer.
            injector (type[Injector]): The member Injector type.
        """
        ...
    def __call__(
        self,
        cls: type[T] |None = None, *,
        namespace: str | None = None,
        strict: bool | None = None,
        deserializer: type[Deserializer] | None = None,
        injector: type[Injector] | None = None
    ) -> Callable[[type[T]], type[T]] | type[T]:
        def decorate(cls: type[T]) -> type[T]:
            SerializerAttributes.make_serializable_lazy(
                cls,
                namespace = namespace,
                strict = strict,
                deserializer = deserializer,
                injector = injector
            )
            return cls

        if cls:
            return decorate(cls)
        else:
            return decorate

serializable = SerializableDecorator()