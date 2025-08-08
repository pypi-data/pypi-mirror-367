# pyright: basic
# ruff: noqa
from pytest import raises as assert_raises
from enum import Enum
from typing import Any, cast
from typingutils import AnyType
from decimal import Decimal
from datetime import date, datetime, time, timezone
from copy import deepcopy

from runtime.serialization import BaseSerializer, SerializationException, NotSerializableException, DeserializationException, serializable, resolvable, resolve_as
from runtime.serialization.core.serializer_attributes import serialize_type

from tests.classes.test_type1 import TestType1
from tests.classes.untyped import Untyped1, UntypedStrict, Untyped2, Untyped3, Untyped4
from tests.classes.test_resolvable import ResolvableBase, T1
from tests.formatter import Formatter

def test_typed():
    formatter = Formatter()

    class NotSerializable:
        def __init__(self, prop1: str):
            self.__prop1 = prop1

        @property
        def prop1(self) -> str:
            return self.__prop1

    @serializable
    class Serializable:
        def __init__(self, prop1: NotSerializable):
            self.__prop1 = prop1

        @property
        def prop1(self) -> NotSerializable:
            return self.__prop1

    serializer = BaseSerializer[Serializable](Formatter)
    inst = Serializable(NotSerializable("test"))
    serialized = serializer.serialize(inst)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized


    serializer = BaseSerializer[TestType1](Formatter)
    assert serializer.formatter is formatter

    with assert_raises(SerializationException, match = r"Cannot serialize object of type .* because the value of following non-nullable members are NULL: .*"):
        inst = TestType1()
        setattr(inst, "_TestType1__prop01", None)
        serializer.serialize(inst)


    inst = TestType1()
    serialized = serializer.serialize(inst)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized

    # try to mess up data
    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop11"][0] = 5478
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop12"]["a"] = "error"
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop16"][0] = "error"
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop17"] = [445, 3]
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop17"] = ["error", "error"]
        deserialized = serializer.deserialize(serialized1)

    # make prop19 an empty tuple
    serialized1 = deepcopy(cast(dict, serialized))
    serialized1["prop19"] = []
    deserialized = serializer.deserialize(serialized1)
    assert deserialized.prop19 == ()

def test_untyped():

    with assert_raises(NotSerializableException):
        serializer = BaseSerializer[UntypedStrict](Formatter)

    serializer = BaseSerializer[Untyped1](Formatter)
    inst = Untyped1("abc", 22)
    serialized = serializer.serialize(inst)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized

    inst = Untyped1("abc", TestType1())
    serialized = serializer.serialize(inst)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized

    serializer = BaseSerializer[Untyped2](Formatter)

    with assert_raises(SerializationException, match = r"Untyped dicts can only have primitive keys e.g. strings, ints and/or floats."):
        inst = Untyped2(["abc",2], set([22]), {date.today(): 1, "b": True}, ("a", 2, 3.3) )
        serialized = serializer.serialize(inst)


    inst = Untyped2(["abc",2], set([22]), {"a": 1, "b": True}, ("a", 2, 3.3) )
    serialized = serializer.serialize(inst)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized

    inst.prop1[1] = date.today()
    serialized = serializer.serialize(inst)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized


    # try to mess up data
    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop1"][0]["~value"] = 2314
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop1"][1]["~value"] = "error"
        deserialized = serializer.deserialize(serialized1)


    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop2"][0]["~value"] = "error"
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop3"]["a"]["~value"] = "error"
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop3"]["b"]["~value"] = "error"
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop4"][0]["~value"] = 22
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop4"][1]["~value"] = "error"
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* as type .*"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop4"][2]["~value"] = "error"
        deserialized = serializer.deserialize(serialized1)

    with assert_raises(DeserializationException, match = r"Unable to deserialize value .* due to missing type hints"):
        serialized1 = deepcopy(cast(dict, serialized))
        serialized1["prop4"][0] = {"a": "error"}
        deserialized = serializer.deserialize(serialized1)

def test_union_typed():

    @serializable
    class TestBasic1:
        def __init__(self, prop1: int|str):
            self.__prop1 = prop1


        @property
        def prop1(self) -> int|str:
            return self.__prop1

    test = TestBasic1("test")
    serializer = BaseSerializer[TestBasic1](Formatter)
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized
    assert deserialized.prop1 == test.prop1
    assert TestBasic1 == type(deserialized)

    with assert_raises(DeserializationException, match = r"Unable to deserialize member .*"):
        cast(dict[str, Any], serialized)["prop1"] = datetime.now()
        deserialized = serializer.deserialize(serialized)
        reserialized = serializer.serialize(deserialized)

    with assert_raises(DeserializationException, match = r"Unable to deserialize member .*"):
        cast(dict[str, Any], serialized)["prop1"] = 436.55673456
        deserialized = serializer.deserialize(serialized)
        reserialized = serializer.serialize(deserialized)

    @serializable
    class TestBasicRef1:
        def __init__(self, prop1: str):
            self.__prop1 = prop1


        @property
        def prop1(self) -> str:
            return self.__prop1

    @serializable
    class TestBasicRef2:
        def __init__(self, prop1: int):
            self.__prop1 = prop1


        @property
        def prop1(self) -> int:
            return self.__prop1


    @serializable
    class TestBasic2:
        def __init__(self, prop1: int|str|TestBasicRef1|TestBasicRef2):
            self.__prop1 = prop1


        @property
        def prop1(self) -> int|str|TestBasicRef1|TestBasicRef2:
            return self.__prop1


    test = TestBasic2(TestBasicRef1("test"))
    serializer = BaseSerializer[TestBasic2](Formatter)
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized
    assert isinstance(test.prop1, TestBasicRef1)
    assert isinstance(deserialized.prop1, TestBasicRef1)
    assert deserialized.prop1.prop1 == test.prop1.prop1
    assert TestBasic2 == type(deserialized)



    @serializable
    class TestBasic3:
        def __init__(self, prop1: int|str|ResolvableBase):
            self.__prop1 = prop1


        @property
        def prop1(self) -> int|str|ResolvableBase:
            return self.__prop1


    test = TestBasic3(T1(prop1 = "test"))
    serializer = BaseSerializer[TestBasic3](Formatter)
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized
    assert isinstance(test.prop1, T1)
    assert isinstance(deserialized.prop1, T1)
    assert deserialized.prop1.prop1 == test.prop1.prop1
    assert TestBasic3 == type(deserialized)

    @serializable
    class TestBasicRef3(TestBasicRef1):
        pass

    @serializable
    class TestBasic4:
        def __init__(self, prop1: int|str|TestBasicRef1):
            self.__prop1 = prop1


        @property
        def prop1(self) -> int|str|TestBasicRef1:
            return self.__prop1


    test = TestBasic4(TestBasicRef3(prop1 = "test"))
    serializer = BaseSerializer[TestBasic4](Formatter)
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized
    assert isinstance(test.prop1, TestBasicRef3)
    assert isinstance(deserialized.prop1, TestBasicRef3)
    assert deserialized.prop1.prop1 == test.prop1.prop1
    assert TestBasic4 == type(deserialized)



    @serializable
    class TestTuple:
        def __init__(self, prop1: tuple[int|str|date, ...], prop2: tuple[int|str|date, int|str|date]):
            self.__prop1 = prop1
            self.__prop2 = prop2

        @property
        def prop1(self) -> tuple[int|str|date, ...]:
            return self.__prop1

        @property
        def prop2(self) -> tuple[int|str|date, int|str|date]:
            return self.__prop2

    test = TestTuple(( 1, "abc", date.today()), ( "defg", 44 ))

    serializer = BaseSerializer[TestTuple](Formatter)
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized
    assert deserialized.prop1 == test.prop1
    assert deserialized.prop2 == test.prop2
    assert TestTuple == type(deserialized)

    test = TestTuple(( ), ( "defg", 44 ))
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized
    assert deserialized.prop1 == test.prop1
    assert deserialized.prop2 == test.prop2
    assert TestTuple == type(deserialized)

    @serializable
    class TestList:
        def __init__(self, prop: list[int|str|date]):
            self.__prop = prop

        @property
        def prop(self) -> list[int|str|date]:
            return self.__prop

    test = TestList([ 1, "abc", date.today()])

    serializer = BaseSerializer[TestList](Formatter)
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized
    assert deserialized.prop == test.prop
    assert TestList == type(deserialized)

    @serializable
    class TestSet:
        def __init__(self, prop: set[int|str|date]):
            self.__prop = prop

        @property
        def prop(self) -> set[int|str|date]:
            return self.__prop

    test = TestSet(set([ 1, "abc", date.today()]))

    serializer = BaseSerializer[TestSet](Formatter)
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    # assert serialized == reserialized due to problems with ordering of the sets, this tests is not applicable
    assert deserialized.prop == test.prop
    assert TestSet == type(deserialized)

    test = TestSet(set())
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert deserialized.prop == test.prop
    assert TestSet == type(deserialized)

    @serializable
    class TestDict:
        def __init__(self, prop: dict[str, int|str|date]):
            self.__prop = prop

        @property
        def prop(self) -> dict[str, int|str|date]:
            return self.__prop

    test = TestDict({ "p1": 1, "p2": "abc", "p3": date.today()})

    serializer = BaseSerializer[TestDict](Formatter)
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized
    assert deserialized.prop["p1"] == test.prop["p1"]
    assert deserialized.prop["p2"] == test.prop["p2"]
    assert deserialized.prop["p3"] == test.prop["p3"]
    assert TestDict == type(deserialized)

    test = TestDict({})
    serialized = serializer.serialize(test)
    deserialized = serializer.deserialize(serialized)
    reserialized = serializer.serialize(deserialized)
    assert serialized == reserialized
    assert TestDict == type(deserialized)

def test_wrong_content_types():

    @serializable
    class TTuple:
        prop1: tuple[str]

    @serializable
    class TList:
        prop1: list[str]

    @serializable
    class TSet:
        prop1: set[str]

    @serializable
    class TDict:
        prop1: dict[str, str]

    inst = TTuple()
    inst.prop1 = (1,2) # pyright: ignore
    serializer = BaseSerializer[TTuple](Formatter)
    with assert_raises(SerializationException, match = r"Value .* cannot be serialized as.*"):
        serializer.serialize(inst)

    inst = TList()
    inst.prop1 = [1,2] # pyright: ignore
    serializer = BaseSerializer[TList](Formatter)
    with assert_raises(SerializationException, match = r"Value .* cannot be serialized as.*"):
        serializer.serialize(inst)

    inst = TSet()
    inst.prop1 = set([1,2]) # pyright: ignore
    serializer = BaseSerializer[TSet](Formatter)
    with assert_raises(SerializationException, match = r"Value .* cannot be serialized as.*"):
        serializer.serialize(inst)

    inst = TDict()
    inst.prop1 = {"a": 1, "b": 2} # pyright: ignore
    serializer = BaseSerializer[TDict](Formatter)
    with assert_raises(SerializationException, match = r"Value .* cannot be serialized as.*"):
        serializer.serialize(inst)

    inst.prop1 = {1: "a", 2: "b"} # pyright: ignore
    serializer = BaseSerializer[TDict](Formatter)
    with assert_raises(SerializationException, match = r"Value .* cannot be serialized as.*"):
        serializer.serialize(inst)

# def test_resolving():
#     class SubType(Enum):
#         T1 = 1
#         T2 = 2
#         T3 = 3

#     @serializable
#     @resolvable
#     class Base:
#         def __init__(self, subtype: SubType):
#             self.__subtype = subtype

#         @property
#         def subtype(self) -> SubType:
#             return self.__subtype

#     @serializable
#     class Derived(Base):
#         def __init__(self, subtype: SubType):
#             self.__subtype = subtype

#         @property
#         def subtype(self) -> SubType:
#             return self.__subtype

#     @resolve_as(Base, lambda base: base.subtype == SubType.T1)
#     @serializable(deserializer=KwargsDeserializer)
#     class T1(Base):
#         def __init__(self, **kwargs: Any):
#             super().__init__(SubType.T1)
#             self.__prop1 = kwargs["prop1"]

#         @property
#         def prop1(self) -> str:
#             return self.__prop1

#     @resolve_as(Base, lambda base: base.subtype == SubType.T2)
#     @serializable(deserializer=KwargsDeserializer)
#     class T2(Base):
#         def __init__(self, **kwargs: Any):
#             super().__init__(SubType.T2)
#             self.__prop1 = kwargs["prop1"]

#         @property
#         def prop1(self) -> int:
#             return self.__prop1


#     @resolve_as(Base, lambda base: base.subtype == SubType.T3)
#     @serializable(deserializer=KwargsDeserializer)
#     class T3(Derived):
#         def __init__(self, **kwargs: Any):
#             super().__init__(SubType.T3)
#             self.__prop1 = kwargs["prop1"]

#         @property
#         def prop1(self) -> str:
#             return self.__prop1

#     @resolve_as(Base, lambda base: base.subtype == 4)
#     @serializable(deserializer=KwargsDeserializer)
#     class T4(Derived):
#         def __init__(self, **kwargs: Any):
#             super().__init__(100) # pyright: ignore[reportArgumentType]
#             self.__prop1 = kwargs["prop1"]

#         @property
#         def prop1(self) -> str:
#             return self.__prop1

#     test1 = T1(prop1="sdg")

#     @serializable
#     class Base1:
#         def __init__(self, subtype: SubType):
#             self.__subtype = subtype

#         @property
#         def subtype(self) -> SubType:
#             return self.__subtype

#     @serializable(deserializer=KwargsDeserializer)
#     class T31(Base1):
#         def __init__(self, **kwargs: Any):
#             super().__init__(SubType.T3)
#             self.__prop1 = kwargs["prop1"]

#         @property
#         def prop1(self) -> str:
#             return self.__prop1