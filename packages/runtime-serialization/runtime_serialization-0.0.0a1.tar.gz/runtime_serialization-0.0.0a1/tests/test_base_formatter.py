# pyright: basic
# ruff: noqa
from pytest import raises as assert_raises
from base64 import b64encode
from typing import Any
from typingutils import AnyType
from decimal import Decimal
from datetime import date, datetime, time, timezone

from runtime.serialization.core.base_formatter import BaseFormatter, CONTEXT
from runtime.serialization.core.serializer_attributes import serialize_type

from tests.classes.test_type1 import TestEnum, TestFlag

ASSERTIONS: list[tuple[tuple[Any, AnyType], tuple[Any, bool], bool]] = [
    ((str, type), (serialize_type(str), True), False),
    ((1, int), (1, True), True),
    ((1.1, float), (1.1, True), True),
    ((Decimal(1.1).normalize(context=CONTEXT), Decimal), ("1.1", True), True),
    ((True, bool), (True, True), True),
    ((False, bool), (False, True), True),
    ((1, bool), (True, True), True),
    ((0, bool), (False, True), True),
    ((True, int), (1, True), False),
    ((False, int), (0, True), False),
    (("abc", str), ("abc", True), True),
    ((b"a0ff", bytes), (b64encode(b"a0ff").decode("utf8"), True), True),
    ((date(2000,1,1), date), ("2000-01-01", True), True),
    ((datetime(2000,1,1,12,10,15), datetime), ("2000-01-01T12:10:15", True), True),
    ((datetime(2000,1,1,12,10,15, tzinfo=timezone.utc), datetime), ("2000-01-01T12:10:15+00:00", True), True),
    ((time(12,10,15), time), ("12:10:15", True), True),
    ((None, str), (None, False), True),
    ((None, str | None), (None, True), True),
    ((None, type[Any]), (None, True), True),
    ((TestEnum.T1, TestEnum), ("T1", True), True),
    ((TestFlag.T2 | TestFlag.T4, TestFlag), (TestFlag.T2+TestFlag.T4, True), True),
]

def test_encode():
    formatter = BaseFormatter()

    for (value, membertype), (expected, success), _ in ASSERTIONS:
        result = formatter.encode(value, membertype)
        assert result == (expected, success)


def test_decode():
    formatter = BaseFormatter()

    for (expected, membertype), (value, _), decodable in ASSERTIONS:
        if decodable:
            result = formatter.decode(value, membertype)
            assert result == (expected, True)
