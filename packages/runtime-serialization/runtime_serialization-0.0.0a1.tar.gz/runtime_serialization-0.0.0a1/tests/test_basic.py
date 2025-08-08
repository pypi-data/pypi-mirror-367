# pyright: basic
# ruff: noqa
from __future__ import annotations
from pytest import raises as assert_raises
from dataclasses import dataclass
from datetime import datetime, date
from typing import TypeVar, Generic, Any, cast
from enum import Enum
import numpy
from delegate.pattern import delegate
from delegate.events import Event, Channel

from runtime.serialization import (
    is_serializable, make_serializable, serializable, ignore, resolve_as, resolvable,
    DefaultDeserializer, KwargsDeserializer, BaseSerializer, Injector, Member,
    DeserializationException, SerializationException, NotSerializableException, CircularReferenceException
)
from runtime.serialization.core.base_serializer import serialize, deserialize
from runtime.serialization.core.decorators.type_resolving.resolve_as_decorator import resolve
from runtime.serialization.core.serializer_attributes import SerializerAttributes

from tests.formatter import Formatter
from tests.classes.test_type1 import TestEnum, TestType1
from tests.classes.test_type2 import TestType2
from tests.classes.test_type3 import TestType3
from tests.classes.test_type4 import TestType4
from tests.classes.test_type5 import TestType5
from tests.classes.test_type6 import TestType6
from tests.classes.test_type7_8 import TestType7, TestType8
from tests.classes.custom_list import CustomList, CustomSequence
from tests.classes.custom_dict import CustomDict, CustomMapping
from tests.classes.custom_set import CustomSet


T = TypeVar('T')


def test_baseclass_deserialization():
    test = TestType3()
    serializer = BaseSerializer[TestType3](Formatter)
    ser = serializer.serialize(test)
    deser = serializer.deserialize(ser)
    assert TestType3 == type(deser)


def test_null_property():
    @serializable(deserializer=DefaultDeserializer)
    class TestNullProperty:
        def __init__(self, prop1: str):
            self.__prop1: str = prop1

        @property
        def prop1(self) -> str:
            return self.__prop1

    test_ok = TestNullProperty("Test")
    serialize(test_ok, None, Formatter)

    test_fail = TestNullProperty(None) # pyright: ignore[reportArgumentType]

    with assert_raises(SerializationException):
        serialize(test_fail, None, Formatter)



def test_untyped_property():

    class TestUntypedProperty:
        def __init__(self, prop1):
            self.__prop1: str | None = prop1 or "Test"

        @property
        def prop1(self):
            return self.__prop1

    with assert_raises(NotSerializableException, match = r"Member .* is not annotated/typed"):
        make_serializable(TestUntypedProperty, strict=True)

    make_serializable(TestUntypedProperty)

def test_untyped_ctor():

    class TestUntypedCtor:
        def __init__(self, prop1):
            self.__prop1: str = prop1 or "Test"

        @property
        def prop1(self) -> str:
            return self.__prop1

    with assert_raises(NotSerializableException, match = r"Deserializer cannot deserialize type because type of argument .* doesn't match the member type .*"):
        make_serializable(TestUntypedCtor)



def test_strategies():

    class TestBase:
        def __init__(self, prop1: str, prop2: int| None):
            self.__prop1 = prop1
            self.__prop2 = prop2
            #self.__prop1 = cast(str, kwargs["prop1"]) if "prop1" in kwargs else "abc"
            #self.__prop2: int| None = cast(int, kwargs["prop2"]) if "prop2" in kwargs else None

        @property
        def prop1(self) -> str:
            return self.__prop1
        @property
        def prop2(self) -> int| None:
            return self.__prop2

    @serializable(deserializer=DefaultDeserializer, strict=True)
    class TestStrict(TestBase):
        pass

    @serializable(deserializer=DefaultDeserializer)
    class TestNormal(TestBase):
        pass


    test_strict = TestStrict("Test", 22)
    test_normal = TestNormal("Test", 22)

    ser_strict = serialize(test_strict, None, Formatter)
    ser_normal = serialize(test_normal, None, Formatter)

    deserialize(ser_strict, TestStrict, Formatter)
    deserialize(ser_normal, TestNormal, Formatter)

    with assert_raises(DeserializationException):
        deserialize(ser_normal, TestStrict, Formatter)
    with assert_raises(DeserializationException):
        deserialize({ "prop1": "Test" }, TestStrict, Formatter)
    with assert_raises(DeserializationException):
        deserialize({}, TestNormal, Formatter)


    # try to delete a property
    ser_strict_copy = { **ser_strict }
    del ser_strict_copy["prop1"]
    with assert_raises(DeserializationException):
        deserialize(ser_strict_copy, TestStrict, Formatter)

    ser_normal_copy = { **ser_normal }
    del ser_normal_copy["prop1"]
    with assert_raises(DeserializationException):
        deserialize(ser_normal_copy, TestNormal, Formatter)


    # try to add a property
    ser_strict_copy = { **ser_strict, **{ "test": "test1" } }
    with assert_raises(DeserializationException):
        deserialize(ser_strict_copy, TestStrict, Formatter)

    ser_normal_copy = { **ser_normal, **{ "test": "test1" } }
    deserialize(ser_normal_copy, TestNormal, Formatter)

    # try to change a property
    ser_strict_copy = { **ser_strict }
    ser_strict_copy["prop2"] = "abcdefg"
    with assert_raises(DeserializationException):
        deserialize(ser_strict_copy, TestStrict, Formatter)

    ser_normal_copy = { **ser_normal }
    ser_normal_copy["prop2"] = "abcdefg"
    with assert_raises(DeserializationException):
        deserialize(ser_normal_copy, TestNormal, Formatter)

    @dataclass
    class TestPoorlyTyped1:
        prop1: list
    @dataclass
    class TestPoorlyTyped2:
        prop1: list

    make_serializable(TestPoorlyTyped1)

    with assert_raises(NotSerializableException, match=r"Deserializer cannot deserialize type because type of member.* is a non-subscripted generic type which is not allowed in strict mode"):
        make_serializable(TestPoorlyTyped2, strict=True)

def test_nested():

    @serializable(deserializer=DefaultDeserializer)
    class TestSubClass:
        def __init__(self, prop: int):
            self.__prop = prop


        @property
        def prop(self) -> int:
            return self.__prop

        @prop.setter
        def prop(self, value: int):
            self.__prop = value


    @serializable(deserializer=DefaultDeserializer)
    class TestSubClass1(TestSubClass):
        pass

    @serializable(deserializer=DefaultDeserializer)
    class TestClass:
        def __init__(self, prop: TestSubClass):
            self.__prop = prop


        @property
        def prop(self) -> TestSubClass:
            return self.__prop

        @prop.setter
        def prop(self, value: TestSubClass):
            self.__prop = value

    obj1= TestClass(TestSubClass1(346))
    ser1 = serialize(obj1, None, Formatter)
    deser1 = deserialize(ser1, TestClass, Formatter)
    reser1 = serialize(deser1, None, Formatter)
    assert ser1 == reser1

    # ser2 = serialize(obj2)
    # deser2 = deserialize(ser2, TestClass)
    # reser2 = serialize(deser2)
    # assert ser2 == reser2

    # assert ser1 == ser2
    # assert reser1 == reser2

def test_derived_types():

    @serializable(deserializer=DefaultDeserializer)
    class TestClass:
        def __init__(self, prop1: int, prop2: float, prop3: bool):
            self.__prop1 = prop1
            self.__prop2 = prop2
            self.__prop3 = prop3


        @property
        def prop1(self) -> int:
            return self.__prop1

        @property
        def prop2(self) -> float:
            return self.__prop2

        @property
        def prop3(self) -> bool:
            return self.__prop3

    test = TestClass(numpy.int32(63546), numpy.float32(45.4323), numpy.bool(True)) # pyright: ignore[reportArgumentType]
    ser = serialize(test, None, Formatter)
    deser = deserialize(ser, TestClass, Formatter)
    reser = serialize(deser, None, Formatter)
    assert ser == reser

def test_properties_and_fields():
    test = TestType5()
    ser = serialize(test, None, Formatter)
    deser = deserialize(ser, TestType5, Formatter)
    reser = serialize(deser, None, Formatter)
    assert ser == reser
    assert test.prop1 == deser.prop1
    assert test.prop2 == deser.prop2
    assert test.prop3 == deser.prop3
    assert test.prop4 == deser.prop4
    assert test.prop5 == deser.prop5


def test_dataclass():
    test1 = TestType6("Test", 4572, 445.9)
    ser1 = serialize(test1, TestType6, Formatter)
    deser1 = deserialize(ser1, TestType6, Formatter)
    reser1 = serialize(deser1, TestType6, Formatter)
    assert ser1 == reser1
    assert test1.prop1 == deser1.prop1
    assert test1.prop2 == deser1.prop2
    assert test1.prop3 == deser1.prop3

    test2 = TestType7(CustomList())
    ser2 = serialize(test2, TestType7, Formatter)
    deser2 = deserialize(ser2, TestType7, Formatter)
    _reser2 = serialize(deser2, TestType7, Formatter)
    _x=0


def test_circular_dependencies():
    class Test3:
        ref: Test1

    @serializable
    class Test2:
        ref: Test3

    @serializable
    class Test1:
        ref: Test2


    test = Test3()
    test.ref = Test1()
    test.ref.ref = Test2()
    test.ref.ref.ref = test

    make_serializable(Test3)
    with assert_raises(CircularReferenceException):
        serialize(test, Test3, Formatter)

    @serializable
    class Test6:
        ref: Test4

    @serializable
    class Test5:
        ref: Test6

    @serializable
    class Test4:
        ref: Test5

    test = Test4()
    test.ref = Test5()
    test.ref.ref = Test6()
    test.ref.ref.ref = test

    with assert_raises(CircularReferenceException):
        serialize(test, Test4, Formatter)

    @serializable
    class Test7:
        pass
    @serializable
    class Test8:
        list: list[Test7]

    test = Test8()
    test.list = [Test7(), Test7()]
    serialize(test, Test8, Formatter)

    test = Test8()
    test1 = Test7()
    test.list = [test1,test1]
    with assert_raises(CircularReferenceException):
        serialize(test, Test8, Formatter)



def test_variadic_tuples():
    @serializable
    class Test1:
        def __init__(self, prop1: tuple[str, ...]):
            self.__prop1 = prop1

        @property
        def prop1(self) -> tuple[str, ...]:
            return self.__prop1

    serializer = BaseSerializer[Test1](Formatter)
    inst = Test1(("abc","def"))
    ser = serializer.serialize(inst)
    deser = serializer.deserialize(ser)
    reser = serializer.serialize(deser)
    assert ser == reser

def test_union_properties():
    @serializable
    class Test1:
        def __init__(self, prop1: str|int, prop2: str):
            self.__prop1 = prop1
            self.__prop2 = prop2

        @property
        def prop1(self) -> str|int:
            return self.__prop1

        @property
        def prop2(self) -> str:
            return self.__prop2

    @serializable
    class Test2:
        def __init__(self, prop1: str|int|None, prop2: str):
            self.__prop1 = prop1
            self.__prop2 = prop2

        @property
        def prop1(self) -> str|int|None:
            return self.__prop1

        @property
        def prop2(self) -> str:
            return self.__prop2

    @serializable
    class Test3:
        def __init__(self, prop1: str|int|None, prop2: str):
            self.__prop1 = prop1
            self.__prop2 = prop2

        @property
        def prop1(self) -> str|int|None:
            return self.__prop1

        @property
        def prop2(self) -> str:
            return self.__prop2

    serializer = BaseSerializer[Test1](Formatter)

    for inst in [
        Test1("Test1", "Test1"),
        Test1(1, "Test1"),
    ]:
        ser = serializer.serialize(inst)
        deser = serializer.deserialize(ser)
        reser = serializer.serialize(deser)
        assert ser == reser


    serializer = BaseSerializer[Test2](Formatter)

    for inst in [
        Test2("Test2", "Test2"),
        Test2(2, "Test2"),
        Test2(None, "Test2"),
    ]:
        ser = serializer.serialize(inst)
        deser = serializer.deserialize(ser)
        reser = serializer.serialize(deser)
        assert ser == reser

    serializer = BaseSerializer[Test3](Formatter)

    for inst in [
        Test3("Test3", "Test3"),
        Test3(3, "Test3"),
        Test3(None, "Test3")
    ]:
        ser = serializer.serialize(inst)
        deser = serializer.deserialize(ser)
        reser = serializer.serialize(deser)
        assert ser == reser


    @serializable
    class Test5:
        def __init__(self, prop1: str):
            self.__prop1 = prop1

        @property
        def prop1(self) -> str:
            return self.__prop1

    @serializable
    class Test4:
        def __init__(self, prop1: str|Test5):
            self.__prop1 = prop1

        @property
        def prop1(self) -> str|Test5:
            return self.__prop1

    serializer = BaseSerializer[Test4](Formatter)

    for inst in [
        Test4("Test4"),
        Test4(Test5("Test5")),
    ]:
        ser = serializer.serialize(inst)
        deser = serializer.deserialize(ser)
        reser = serializer.serialize(deser)
        assert ser == reser



def test_serialization_exception():

    @serializable
    class TestA:
        def __init__(self, propA1: TestB):
            self.__propA1 = propA1

        @property
        def propA1(self) -> TestB:
            return self.__propA1

    @serializable
    class TestB:
        def __init__(self, propB1: TestC, propB2: list[int], propB3: dict[str, int]):
            self.__propB1 = propB1
            self.__propB2 = propB2
            self.__propB3 = propB3

        @property
        def propB1(self) -> TestC:
            return self.__propB1

        @property
        def propB2(self) -> list[int]:
            return self.__propB2

        @property
        def propB3(self) -> dict[str, int]:
            return self.__propB3

    @serializable
    class TestC:
        def __init__(self, propC1: int):
            self.__propC1 = propC1

        @property
        def propC1(self) -> int:
            return self.__propC1

    try:
        inst = TestA(TestB(TestC(22), [1,2,3], {"a": 1, "b": 2, "c": 3}))
        setattr(inst.propA1.propB1, "_TestC__propC1", "ERROR")
        with assert_raises(SerializationException):
            serialize(inst, TestA, Formatter)
        serialize(inst, TestA, Formatter)
    except SerializationException as ex:
        assert ex.path == "root.propA1.propB1.propC1"

    try:
        inst = TestA(TestB(TestC(22), [1,2,3], {"a": 1, "b": 2, "c": 3}))
        inst.propA1.propB2[1] = "ERROR" # pyright: ignore[reportArgumentType, reportCallIssue]
        # with assert_raises(SerializationException):
        #     serialize(inst, TestA, BaseEncoder)
        serialize(inst, TestA, Formatter)
    except SerializationException as ex:
        assert ex.path == "root.propA1.propB2[1]"

    try:
        inst = TestA(TestB(TestC(22), [1,2,3], {"a": 1, "b": 2, "c": 3}))
        inst.propA1.propB3["b"] = "ERROR" # pyright: ignore[reportArgumentType]
        with assert_raises(SerializationException):
            serialize(inst, TestA, Formatter)
        serialize(inst, TestA, Formatter)
    except SerializationException as ex:
        assert ex.path == "root.propA1.propB3{b}"

    inst = TestA(TestB(TestC(22), [1,2,3], {"a": 1, "b": 2, "c": 3}))

    try:
        ser = serialize(inst, TestA, Formatter)
        ser["propA1"]["propB1"]["propC1"] = "ERROR" # pyright: ignore[reportArgumentType, reportCallIssue, reportIndexIssue, reportOptionalSubscript]
        with assert_raises(DeserializationException):
            deserialize(ser, TestA, Formatter)
        deserialize(ser, TestA, Formatter)
    except DeserializationException as ex:
        assert ex.path == "root.propA1.propB1.propC1"

    try:
        ser = serialize(inst, TestA, Formatter)
        ser["propA1"]["propB2"][1] = "ERROR" # pyright: ignore[reportArgumentType, reportCallIssue, reportIndexIssue, reportOptionalSubscript]
        with assert_raises(DeserializationException):
            deserialize(ser, TestA, Formatter)
        deserialize(ser, TestA, Formatter)
    except DeserializationException as ex:
        assert ex.path == "root.propA1.propB2[1]"

    try:
        ser = serialize(inst, TestA, Formatter)
        ser["propA1"]["propB3"]["b"] = "ERROR" # pyright: ignore[reportArgumentType, reportCallIssue, reportIndexIssue, reportOptionalSubscript]
        with assert_raises(DeserializationException):
            deserialize(ser, TestA, Formatter)
        deserialize(ser, TestA, Formatter)
    except DeserializationException as ex:
        assert ex.path == "root.propA1.propB3{b}"


class TestType(Enum):
    __test__ = False
    T1 = 1
    T2 = 2
    T3 = 3
