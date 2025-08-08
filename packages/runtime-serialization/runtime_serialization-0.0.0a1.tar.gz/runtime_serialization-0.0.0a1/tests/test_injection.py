# pyright: basic
# ruff: noqa
from __future__ import annotations
from pytest import raises as assert_raises
from typing import  Any, cast


from runtime.serialization import serializable, DefaultDeserializer, BaseSerializer, Injector, Member, DeserializationException, SerializationException
from runtime.serialization.core.base_serializer import serialize, deserialize

from tests.formatter import Formatter



def test_injector():
    injected_value = "Injected"
    class Injector1(Injector):
        def try_inject_null_property(self, obj_type: type, member: Member) -> tuple[Any|None, bool]:
            if issubclass(obj_type, TestInject1) and member.name == "prop1":
                return injected_value, True
            elif issubclass(obj_type, TestInject2) and member.name == "prop1":
                return injected_value, True
            elif issubclass(obj_type, TestInject4) and member.name in ("prop1", "prop3"):
                return injected_value, True
            elif issubclass(obj_type, TestInject5) and member.name in ("prop2", "prop3"):
                return injected_value, True
            return None, False

    @serializable(deserializer=DefaultDeserializer, injector=Injector1)
    class TestInject1:
        def __init__(self, prop1: str | None):
            self.__prop1 = prop1

        @property
        def prop1(self) -> str | None:
            return self.__prop1

    @serializable
    @serializable.injector(Injector1)
    @serializable.deserializer(DefaultDeserializer)
    class TestInject2:
        def __init__(self, prop1: str):
            self.__prop1 = prop1

        @property
        def prop1(self) -> str:
            return self.__prop1

    @serializable
    @serializable.injector(Injector1)
    @serializable.deserializer(DefaultDeserializer)
    class TestInject3:
        def __init__(self, prop1: str):
            self.__prop1 = prop1

        @property
        def prop1(self) -> str:
            return self.__prop1

    @serializable(deserializer=DefaultDeserializer, injector=Injector1)
    class TestInject4:
        def __init__(self, prop1: str | None, prop2: str, prop3: int):
            self.__prop1 = prop1
            self.__prop2 = prop2
            self.__prop3 = prop3

        @property
        def prop1(self) -> str | None:
            return self.__prop1

        @property
        def prop2(self) -> str:
            return self.__prop2

        @property
        def prop3(self) -> int:
            return self.__prop3

    @serializable(deserializer=DefaultDeserializer, injector=Injector1)
    class TestInject5:
        def __init__(self, prop1: str | None, prop2: str | None, prop3: int):
            self.__prop1 = prop1
            self.__prop2 = prop2
            self.__prop3 = prop3

        @property
        def prop1(self) -> str | None:
            return self.__prop1

        @property
        def prop2(self) -> str | None:
            return self.__prop2

        @property
        def prop3(self) -> int:
            return self.__prop3

    # inject value on both serialization and deserialization
    test = TestInject1(None)
    serializer = BaseSerializer[TestInject1](Formatter)
    serialized = serializer.serialize(test)
    assert serialized["prop1"] == injected_value
    serialized["prop1"] = None # pyright: ignore[reportIndexIssue]
    deserialized = serializer.deserialize(serialized)
    assert deserialized.prop1 == injected_value


    test = TestInject2("test")
    serializer = BaseSerializer[TestInject2](Formatter)
    serialized = serializer.serialize(test)
    serialized["prop1"] = None # pyright: ignore[reportIndexIssue]
    deserialized = serializer.deserialize(serialized)
    assert deserialized.prop1 == injected_value

    with assert_raises(DeserializationException, match = r"Cannot deserialize type .* from data, because following non-nullable members are NULL: .*"):
        test = TestInject3("test")
        serializer = BaseSerializer[TestInject3](Formatter)
        serialized = serializer.serialize(test)
        serialized["prop1"] = None # pyright: ignore[reportIndexIssue]
        deserialized = serializer.deserialize(serialized)

    serializer = BaseSerializer[TestInject4](Formatter)

    with assert_raises(DeserializationException, match = r"Cannot deserialize type .* from data, because following non-nullable members are NULL: .*"):
        test = TestInject4(None, "test", 22)
        serialized = serializer.serialize(test)
        assert serialized["prop1"] == injected_value
        serialized["prop2"] = None # pyright: ignore[reportIndexIssue]
        deserialized = serializer.deserialize(serialized)

    serializer = BaseSerializer[TestInject5](Formatter)
    test = TestInject5(None, None, 22)
    serialized = serializer.serialize(test)
    assert serialized["prop2"] == injected_value