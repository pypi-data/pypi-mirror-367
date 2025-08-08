from typing import TypeVar, Any, cast
from typingutils import AnyType, get_generic_arguments, is_type, is_subscripted_generic_type, is_variadic_tuple_type, is_union, issubclass_typing, get_type_name
from typingutils.internal import  get_generic_origin
from types import NoneType
from enum import Enum
from collections import abc

from runtime.serialization.core.serializer_attributes_registry import SERIALIZABLE_LOCK, SERIALIZABLE_TYPE_GENERIC_PARAMETERS, SERIALIZABLES
from runtime.serialization.core.not_serializable_exception import NotSerializableException

T = TypeVar("T")

def is_serializable(obj: Any) -> bool:
    """Indicates if object or type is serializable or not (ie. implements the @serializable decorator).
    Primitive types, such as int, str, bool etc. along with types such as lists, tuples and dicts are always serializable

    Args:
        obj (Any): The object or type to check

    Returns:
        bool: True or false
    """
    cls = cast(type[Any], type(obj) if not is_type(obj) else obj)
    generic_args: tuple[AnyType, ...] | None = ()
    non_serializable_args: list[AnyType] | None = []
    origin = cls

    if is_subscripted_generic_type(cls):
        generic_args = get_generic_arguments(cls)
        non_serializable_args = [ arg for arg in generic_args if not is_serializable(arg) ]
        origin = get_generic_origin(cls)

    with SERIALIZABLE_LOCK:
        if origin in SERIALIZABLES:
            return True
        elif is_union(cls):
            return not any([ arg for arg in non_serializable_args if arg is not NoneType ])
        elif issubclass_typing(cls, Enum):
            return True
        else:
            if origin is tuple:
                if is_variadic_tuple_type(cls) and generic_args:
                    return is_serializable(generic_args[0])
                else:
                    return not any(non_serializable_args)
            elif origin in SERIALIZABLE_TYPE_GENERIC_PARAMETERS and SERIALIZABLE_TYPE_GENERIC_PARAMETERS[origin] == len(generic_args):
                return not any(non_serializable_args)
            elif issubclass_typing(origin, list) and len(generic_args) == SERIALIZABLE_TYPE_GENERIC_PARAMETERS[list]:
                return not any(non_serializable_args)
            elif issubclass_typing(origin, (list, set, dict, abc.Mapping, abc.Sequence)) and not generic_args:
                return True
            elif issubclass_typing(origin, set) and len(generic_args) == SERIALIZABLE_TYPE_GENERIC_PARAMETERS[set]:
                return not any(non_serializable_args)
            elif issubclass_typing(origin, abc.Mapping) and len(generic_args) == SERIALIZABLE_TYPE_GENERIC_PARAMETERS[dict]:
                return not any(non_serializable_args)
            elif issubclass_typing(origin, abc.Sequence) and len(generic_args) == SERIALIZABLE_TYPE_GENERIC_PARAMETERS[list]:
                return not any(non_serializable_args)
        return False

def check_serializable(cls: AnyType) -> None:
    """Checks that the type is serializable. Raises an exception if not.

    Args:
        cls (type): The type to check

    Raises:
        NotSerializableException: If type is not serializable
    """
    if not is_serializable(cls):
        raise NotSerializableException(cls)

def serialize_type(cls: AnyType) -> str:
    if cls in SERIALIZABLES:
        return f"{SERIALIZABLES[cls]().type_name}"
    else:
        return get_type_name(cls)
