from collections import abc
from datetime import date, time, datetime
from decimal import Decimal
from typingutils import AnyType, get_type_name
import builtins


from runtime.serialization.core.threading import Lock
from runtime.serialization.core.lazy import Lazy
from runtime.serialization.core.interfaces.serializer_attributes import SerializerAttributes

SERIALIZABLE_LOCK = Lock()
SERIALIZABLE_TYPE_GENERIC_PARAMETERS: dict[AnyType, int] = {
    str: 0,
    int: 0,
    float: 0,
    Decimal: 0,
    bool: 0,
    bytes: 0,
    date: 0,
    datetime: 0,
    time: 0,
    type: 0,
    tuple: 1,
    list: 1,
    set: 1,
    dict: 2,
    abc.Sequence: 1,
    abc.Mapping: 2
}
SERIALIZABLE_TYPE_DEFS: dict[str, AnyType] = {
    **{
        get_type_name(value): value
        for name, value in builtins.__dict__.items()
        if isinstance(value, type) and not name.startswith("__") and not name.endswith("__")
    },
    get_type_name(date): date,
    get_type_name(time): time,
    get_type_name(datetime): datetime,
    get_type_name(Decimal): Decimal,
}
SERIALIZABLES: dict[AnyType, Lazy[SerializerAttributes]] = {}

