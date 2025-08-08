# pyright: basic
# ruff: noqa
from __future__ import annotations
from pytest import raises as assert_raises
from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar, Any, cast
from enum import Enum
from delegate.pattern import delegate, Delegate
from delegate.events import Event, Channel

from runtime.serialization import (
    is_serializable, serializable_delegate, make_serializable, serializable, ignore, resolvable, resolve_as,
    DefaultDeserializer, KwargsDeserializer, BaseSerializer,
    DeserializationException, SerializationException, NotSerializableException
)
from runtime.serialization.core.base_serializer import serialize, deserialize
from runtime.serialization.core.decorators.type_resolving.resolve_as_decorator import resolve
from runtime.serialization.core.decorators.type_resolving.dict_object import DictObject
from runtime.serialization.core.decorators.decorator_exception import DecoratorException
from runtime.serialization.core.serializer_attributes import SerializerAttributes

from tests.formatter import Formatter
from tests.classes.test_resolvable import SubType, ResolvableBase, ResolvableDerived, T1, T2, T3



T = TypeVar('T')

def test_ignore():

    class OnChangeEventDef(Event):
        pass

    class TestDelegate:
        def __get__(self, instance: object, cls: type) -> str:
            return "Test"

    @serializable
    @dataclass
    class TestClass:
        prop1: str

        Event = delegate(Channel[OnChangeEventDef]) # is treated as a delegate, because Delegate[T]() -> Event has a __get__() function
        Dlg = TestDelegate() # is treated as a delegate, because TestDelegate has a __get__() function

        @ignore
        @property
        def prop2(self) -> str:
            return self.prop1 * 2

        @ignore()
        @property
        def prop3(self) -> str:
            return self.prop1 + "test"

    test = TestClass("Test")
    serialized = serialize(test, TestClass, Formatter)
    deserialized = deserialize(serialized, TestClass, Formatter)
    reserialized = serialize(deserialized, TestClass, Formatter)
    assert serialized == reserialized




def test_type_resolving():

    test1 = T1(prop1="sdg")

    @serializable
    class Base1:
        def __init__(self, subtype: SubType):
            self.__subtype = subtype

        @property
        def subtype(self) -> SubType:
            return self.__subtype

    @serializable(deserializer=KwargsDeserializer)
    class T31(Base1):
        def __init__(self, **kwargs: Any):
            super().__init__(SubType.T3)
            self.__prop1 = kwargs["prop1"]

        @property
        def prop1(self) -> str:
            return self.__prop1

    with assert_raises(Exception, match = r"Base class .* is already a registered resolvable"):
        resolvable(ResolvableBase)

    with assert_raises(Exception, match = r"Derived class .* is already defined in resolve chain"):
        resolve_as(ResolvableBase, lambda base: base.subtype == SubType.T3)(T3)

    with assert_raises(Exception, match = r"Base class .* is not defined resolvable"):
        serialized01 = serialize(T31(prop1='2'), Base1, Formatter)
        resolve(Base1, DictObject(cast(dict[str, Any], serialized01)))

    with assert_raises(Exception, match = r"Class .* is not derived from .*"):
        resolve_as(Base1, lambda base: base.subtype == SubType.T3)(T3)


    assert callable(resolvable())

    from runtime.reflection.lite import get_members
    sig1 = get_members(ResolvableBase)
    p1 = sig1.subset_properties()["subtype"]
    sig2 = get_members(Base1)
    p2 = sig2.subset_properties()["subtype"]

    serialized1 = serialize(test1, ResolvableBase, Formatter)
    assert "~type" not in serialized1.keys()
    serialized1 = { key: value for key, value in serialized1.items() if key != "~type" }
    deserialized1 = deserialize(serialized1, ResolvableBase, Formatter)
    reserialized1 = serialize(deserialized1, ResolvableBase, Formatter)
    reserialized1 = { key: value for key, value in reserialized1.items() if key != "~type" }
    assert serialized1 == reserialized1

    test2 = T2(prop1=56)
    serialized2 = serialize(test2, ResolvableBase, Formatter)
    serialized2 = { key: value for key, value in serialized2.items() if key != "~type" }
    deserialized2 = deserialize(serialized2, ResolvableBase, Formatter)
    reserialized2 = serialize(deserialized2, ResolvableBase, Formatter)
    reserialized2 = { key: value for key, value in reserialized2.items() if key != "~type" }
    assert serialized2 == reserialized2

    test3 = T3(prop1="swedeg")
    serialized3 = serialize(test3, ResolvableBase, Formatter)
    serialized3 = { key: value for key, value in serialized3.items() if key != "~type" }
    deserialized3 = deserialize(serialized3, ResolvableBase, Formatter)
    reserialized3 = serialize(deserialized3, ResolvableBase, Formatter)
    reserialized3 = { key: value for key, value in reserialized3.items() if key != "~type" }
    assert serialized3 == reserialized3


    test4 = T3(prop1="swedeg")
    serialized4 = serialize(test4, ResolvableBase, Formatter)
    serialized4 = { key: value for key, value in serialized4.items() if key != "~type" }
    serialized4["subtype"] = 4000

    with assert_raises(DeserializationException, match = r"Unable to deserialize member .*"):
        deserialized4 = deserialize(serialized4, ResolvableBase, Formatter)

    with assert_raises(Exception, match = r"Unable to resolve"):
        resolve(ResolvableBase, DictObject(cast(dict[str, Any], serialized4)))

    @serializable
    class NestingDerived:
        def __init__(self, prop1: int, prop2: ResolvableBase):
            self.__prop1 = prop1
            self.__prop2 = prop2

        @property
        def prop1(self) -> int:
            return self.__prop1

        @property
        def prop2(self) -> ResolvableBase:
            return self.__prop2

    test4 = NestingDerived(35478, T1(prop1="sdggbh"))
    serialized4 = serialize(test4, NestingDerived, Formatter)
    deserialized4 = deserialize(serialized4, NestingDerived, Formatter)
    reserialized4 = serialize(deserialized4, NestingDerived, Formatter)
    reserialized4 = { key: value for key, value in reserialized4.items() if key != "~type" }
    assert serialized4 == reserialized4

def test_serializable():

    @serializable.namespace("test")
    @serializable.strict(True)
    @serializable.deserializer(KwargsDeserializer)
    class Test1:
        def __init__(self, **kwargs: Any):
            self.__prop1 = kwargs["prop1"]

        @property
        def prop1(self) -> int:
            return self.__prop1

    assert not is_serializable(Test1)
    with assert_raises(NotSerializableException):
        SerializerAttributes.get(Test1)
    serializer1 = SerializerAttributes.make_serializable_lazy(Test1)()
    assert is_serializable(Test1)
    assert serializer1.namespace == "test"
    assert serializer1.type_name == "test.Test1"
    assert serializer1.strict
    assert type(serializer1.deserializer) is KwargsDeserializer

    # below impl. is not the intended use of @serializable - intended use is for situations
    # when make_serializable is called later on, and below impl. gives same result as using
    # the @serializable(namespace="test") decorator
    @serializable
    @serializable.namespace("test")
    class Test2:
        def __init__(self, prop1: int):
            self.__prop1 = prop1

        @property
        def prop1(self) -> int:
            return self.__prop1

    assert is_serializable(Test2)
    serializer2 = SerializerAttributes.get(Test2)
    assert serializer2.namespace == "test"
    assert serializer2.type_name == "test.Test2"
    assert not serializer2.strict
    assert type(serializer2.deserializer) is DefaultDeserializer


    with assert_raises(DecoratorException, match = r"Serializable decorator can only be applied once"):
        serializable.namespace("test")(Test2)


def test_serializable_delegate():

    @serializable
    class Test1:
        def __init__(self, prop1: int):
            self._data = {}
            self.__prop1 = prop1

        @property
        def prop1(self) -> int:
            return self.__prop1

        prop2 = add_delegate1(str)


    assert is_serializable(Test1)
    inst1 = Test1(1)
    inst1.prop2 = "abc"

    serialized1 = serialize(inst1, Test1, Formatter)
    assert "prop2" not in serialized1
    deserialized1 = deserialize(serialized1, Test1, Formatter)
    assert deserialized1.prop1 == inst1.prop1
    assert deserialized1.prop2 != inst1.prop2


    class Test2:
        def __init__(self, prop1: int, prop2: str):
            self._data = {}
            self.__prop1 = prop1
            self.prop2 = prop2

        @property
        def prop1(self) -> int:
            return self.__prop1

        prop2: str = add_delegate2(str)

    assert hasattr(Test2, "prop2")
    inst2 = Test2(2, "test")
    inst2.prop2 = "abcdefg"

    with assert_raises(NotSerializableException):
        serialized2 = serialize(inst2, Test2, Formatter)

    serializable(Test2)
    serialized2 = serialize(inst2, Test2, Formatter)

    assert "prop2" in serialized2
    deserialized2 = deserialize(serialized2, Test2, Formatter)
    assert deserialized2.prop1 == inst2.prop1
    assert deserialized2.prop2 == inst2.prop2



def add_delegate1(cls: type[T]) -> T:
    return TestDelegate1[cls](cls) # pyright: ignore[reportReturnType, reportArgumentType]

def add_delegate2(cls: type[T]) -> T:
    return TestDelegate2[cls](cls) # pyright: ignore[reportReturnType, reportArgumentType]

class TestDelegate1(Generic[T]):
    __test__ = False

    def __init__(self, cls: type[T]):
        self.__name = "" # lazy loaded
        self.__type = type(cls)

    def __get__(self, instance: type | object, cls: type[Any]) -> TestDelegate1[T] | T:
        if isinstance(instance, type) and issubclass(instance, cls):
            return self
        else:
            if not self.__name:
                for base_cls in cls.__mro__:
                    attrs = [ (k,v) for k,v in base_cls.__dict__.items() if v == self ]
                    if any(attrs):
                        cls = base_cls
                        self.__name = attrs[0][0]
                        break

            inst_data = cast(dict[str, Any], getattr(instance, "_data"))
            return cast(T, inst_data[self.__name] if self.__name in inst_data else None)


    def __set__(self, instance: object, value: T) -> None:
        if not self.__name:
            self.__get__(instance, type(instance))
        inst_data = cast(dict[str, Any], getattr(instance, "_data"))
        inst_data[self.__name] = value

@serializable_delegate
class TestDelegate2(Generic[T]):
    __test__ = False

    def __init__(self, cls: type[T]):
        self.__shim = None
        self.__name = "" # lazy loaded
        self.__type = type(cls)
        self.__readonly = False

    def __get__(self, instance: type | object, cls: type[Any]) -> TestDelegate2[T] | T:
        if isinstance(instance, type) and issubclass(instance, cls):
            return self
        elif instance is None: # return a property shim
            if self.__shim is None:
                dyn_prop = self

                def fget(self):
                    return dyn_prop.__get__(self, self if isinstance(self, type) else type(self))
                fget.__annotations__ = { "return": self.__type }

                if not self.__readonly:
                    def fset(self, value: T):
                        dyn_prop.__set__(self, value)
                    fset.__annotations__ = { "value": self.__type }

                    self.__shim = property(fget, fset)
                else:
                    self.__shim = property(fget)

            return self.__shim # pyright: ignore[reportReturnType]

        else:
            if not self.__name:
                for base_cls in cls.__mro__:
                    attrs = [ (k,v) for k,v in base_cls.__dict__.items() if v == self ]
                    if any(attrs):
                        cls = base_cls
                        self.__name = attrs[0][0]
                        break

            inst_data = cast(dict[str, Any], getattr(instance, "_data"))
            return cast(T, inst_data[self.__name] if self.__name in inst_data else None)


    def __set__(self, instance: object, value: T) -> None:
        if not self.__name: # delegate isn't fully setup (its name isn't known)
            self.__get__(instance, type(instance))
        inst_data = cast(dict[str, Any], getattr(instance, "_data"))
        inst_data[self.__name] = value
