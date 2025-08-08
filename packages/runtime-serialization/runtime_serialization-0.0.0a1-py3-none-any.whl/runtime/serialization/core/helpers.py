from __future__ import annotations
from typing import TypeVar, Annotated, Any, cast
from types import NoneType
from typingutils import TypeParameter, AnyType, get_type_name
from runtime.reflection.lite import Property, Field, Delegate, MemberFilter, get_members as get_members_reflection


from runtime.serialization.core.decorators.ignore_decorator import IGNORED
from runtime.serialization.core.decorators.serializable.serializable_delegate_decorator import SERIALIZABLE_DELEGATES
from runtime.serialization.core.member import Member

T = TypeVar("T")

Result = Annotated[tuple[T | None, bool], "The result and success of an operation"]

def is_primitive(obj: Any) -> bool:
    """Indicates if object or type is primitive

    Arguments:
        obj {object | type} -- The object or type to check

    Returns:
        bool -- True or false
    """
    obj_type = obj if isinstance(obj, type) else type(obj)
    return obj_type in (NoneType, bool, int, float, str)

def get_members(cls: type, strict:  bool) -> tuple[Member, ...]:
    """Returns all class members, which are not delegates or functions, and not decorated with the @ignore decorator

    Args:
        cls (type): The serializable class

    Returns:
        tuple[Member]: A tuple of members
    """

    reflection = get_members_reflection(cls, filter = MemberFilter.PROPERTIES | MemberFilter.FIELDS_AND_VARIABLES | MemberFilter.DELEGATES)

    members: list[Member] = []

    for _, (info, member) in reflection.items():
        if isinstance(member, Property) and member.reflected not in IGNORED:
            return_type = member.property_type if strict else member.property_type
            members.append(Member.create(cls, info.name, return_type))
        elif isinstance(member, Field) and member.field_type:
            return_type = member.field_type if strict else member.field_type
            members.append(Member.create(cls, info.name, return_type))
        elif isinstance(member, Delegate) and type(member.reflected) in SERIALIZABLE_DELEGATES and member.reflected not in IGNORED:
            return_type = member.delegate_type if strict else member.delegate_type
            members.append(Member.create(cls, info.name, return_type))
        elif isinstance(member, Delegate):
            pass
        else:
            pass

    return tuple(members)

def construct_generic_type(origin: TypeParameter, *generic_arguments: AnyType) -> type:
    if hasattr(origin, "__class_getitem__"):
        return cast(type, getattr(origin, "__class_getitem__")(generic_arguments))
    else:
        raise Exception(f"Type {get_type_name(origin)} is not generic!") # pragma: no cover
