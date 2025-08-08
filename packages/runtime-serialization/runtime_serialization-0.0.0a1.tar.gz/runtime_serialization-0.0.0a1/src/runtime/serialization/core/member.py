from __future__ import annotations
from typing import TypeVar, Any, cast, Callable
from typingutils import AnyType, get_optional_type

from runtime.serialization.core.member_type import MemberType
from runtime.serialization.core.readonly_exception import ReadonlyException

T = TypeVar("T")

class Member():
    __slots__ = ["__name", "__member_type", "__return_type", "__getter", "__setter", "__nullable"]

    def __init__(
        self,
        name: str,
        member_type: MemberType,
        return_type: AnyType,
        getter: Callable[[object], Any],
        setter: Callable[[object, Any], None] | None,
        nullable: bool = True
    ):
        self.__name = name
        self.__member_type = member_type
        self.__return_type = return_type or None
        self.__getter = getter
        self.__setter = setter
        self.__nullable = nullable


    @property
    def name(self) -> str:
        return self.__name

    @property
    def return_type(self) -> AnyType | None:
        return self.__return_type

    @property
    def member_type(self) -> MemberType:
        return self.__member_type

    @property
    def is_readonly(self) -> bool:
        return not self.__setter

    @property
    def is_nullable(self) -> bool:
        return self.__nullable

    def get_value(self, obj: object) -> object:
        return self.__getter(obj)

    def set_value(self, obj: object, value: Any) -> None:
        if not self.__setter:
            raise ReadonlyException(self.__name) # pragma: no cover

        self.__setter(obj, value)

    def __repr__(self):
        return f"Member '{self.__name}'"

    @staticmethod
    def create(target_type: type, name: str, annotation: type) -> Member:
        getter: Callable[[object], Any]
        setter: Callable[[object, Any], None] | None

        if hasattr(target_type, name) and isinstance(getattr(target_type, name), property):
            property_obj = cast(property, getattr(target_type, name))
            member_type = MemberType.PROPERTY
            getter = property_obj.__get__
            setter = property_obj.__set__ if property_obj.fset else None
        else:
            member_type = MemberType.FIELD
            def fget(obj: object) -> Any:
                return getattr(obj, name) if hasattr(obj, name) else None
            def fset(obj: object, value: Any) -> None:
                return setattr(obj, name, value)
            getter = fget
            setter = fset

        return_type, nullable = get_optional_type(annotation)

        return Member(
            name,
            member_type,
            cast(type[Any], return_type),
            getter,
            setter,
            nullable
        )

