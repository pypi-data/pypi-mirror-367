from base64 import b64encode, b64decode
from typing import SupportsFloat, SupportsInt, Callable, Any, cast
from enum import Enum, IntEnum, IntFlag
from decimal import Decimal, Context
from datetime import date, datetime, time
from dateutil.parser import parse as parse_datetime
from collections.abc import Mapping
from typingutils import AnyType, isinstance_typing, issubclass_typing, is_union
from typingutils.internal import get_union_types

from runtime.serialization.core.protocols.supports_bool import SupportsBool
from runtime.serialization.core.serializer_attributes import serialize_type
from runtime.serialization.core.helpers import Result, is_primitive
from runtime.serialization.core.primitives import Primitive, Primitives

CONTEXT = Context(prec=8)

class BaseFormatter:
    __slots__ = [ ]

    @staticmethod
    def encode(value: Any, member_type: AnyType | None) -> Result[Primitives]:
        # if value isn't an instance of the member type, it may be converted
        if member_type is not None and not isinstance_typing(value, member_type):
            if member_type is bool and isinstance(value, SupportsBool):
                value = bool(value)
            elif member_type is int and isinstance(value, SupportsInt):
                value = int(value)
            elif member_type is float and isinstance(value, SupportsFloat):
                value = float(value)
            # elif member_type is str:
            #     value = str(value) # just convert anything to its string representation

        if member_type is not None and isinstance_typing(value, member_type):
            if value is None:
                result = value
            elif isinstance(value, bytes):
                result = b64encode(value).decode("utf8")
            elif isinstance(value, (IntEnum, IntFlag)):
                result = int(value)
            elif isinstance(value, Enum):
                result = value.name
            elif isinstance(value, type):
                result = serialize_type(value)
            elif isinstance(value, bool): # value may be masking a bool type
                result = bool(value)
            elif isinstance(value, int): # value may be masking an int type
                result = int(value)
            elif isinstance(value, float): # value may be masking a float type
                result = float(value)
            elif isinstance(value, Decimal):
                result = f"{value.normalize(CONTEXT):g}" # suppress scientific notation and remove trailing zeros
            elif isinstance(value, (date, datetime, time)):
                result = value.isoformat()
            elif isinstance(value, Primitive): # value is a genuine supported type
                result = value
            else:
                return None, False

            return result, True
        else:
            return None, False

    @staticmethod
    def decode(value: Any, member_type: AnyType | None) -> Result[Any]:
        try:
            if is_union(member_type): # pyright: ignore[reportArgumentType]
                for uniontype in [ t for t in get_union_types(member_type) if not is_primitive(t) ]: # pyright: ignore[reportArgumentType]
                    if isinstance(value, str) and uniontype in (datetime, date, time):
                        return BaseFormatter.decode(value, uniontype)

            if value is None:
                result = value
            elif member_type and issubclass_typing(member_type, Primitive) and isinstance_typing(value, member_type):
                result = value
            elif member_type is bytes:
                result = b64decode(cast(bytes, value))
            elif member_type is Decimal and isinstance(value, (str, int, float)):
                result = Decimal(value)
            elif member_type and issubclass_typing(member_type, Enum):
                result = cast(Mapping[str, Any], member_type)[value] if isinstance(value, str) else cast(Callable[[Any], Any], member_type)(value)
            elif member_type is datetime:
                result = parse_datetime(cast(str, value))
            elif member_type is date:
                result = date.fromisoformat(cast(str, value))
            elif member_type is time:
                result = time.fromisoformat(cast(str, value))
            else:
                return None, False

            return result, True

        except ValueError:
            return None, False
