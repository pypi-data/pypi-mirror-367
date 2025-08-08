# pyright: basic
# ruff: noqa
from pytest import raises as assert_raises
from typing import TypeVar, Generic, Any, cast

from runtime.serialization.core.serializer_attributes import SerializerAttributes

from runtime.serialization import serializable, DefaultDeserializer, Injector, Member, NotSerializableException
from runtime.serialization.core.base_serializer import serialize, deserialize

from tests.formatter import Formatter



def test_is_singleton():
    attr = SerializerAttributes.create(Test1)()
    assert attr is SerializerAttributes.create(Test1)()

def test_generic():
    attr2 = SerializerAttributes.create(Test2[str])()
    attr1 = SerializerAttributes.create(list[int])()
    with assert_raises(NotSerializableException, match="Serializable attributes are incompatible with non-subscripted generic types"):
        SerializerAttributes.create(list[TypeVar("T")])()
    with assert_raises(NotSerializableException, match="Serializable attributes are incompatible with non-subscripted generic types"):
        SerializerAttributes.create(Test2)()


T = TypeVar("T")
# @serializable.namespace("test")
# @serializable.strict(True)
# @serializable.deserializer(DefaultDeserializer)
class Test1:
    __test__ = False
    def __init__(self, prop1: int):
        self.__prop1 = prop1

    @property
    def prop1(self) -> int:
        return self.__prop1

class Test2(Generic[T]):
    __test__ = False
    def __init__(self, prop1: T):
        self.__prop1 = prop1

    @property
    def prop1(self) -> T:
        return self.__prop1