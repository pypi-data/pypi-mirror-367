from typing import Any, cast
from typingutils import AnyType, issubclass_typing
from collections.abc import Sequence, Mapping

from runtime.serialization.core.helpers import Result
from runtime.serialization.core.primitives import Primitives
from runtime.serialization.core.base_formatter import BaseFormatter
from runtime.serialization.core.interfaces.formatter import Formatter as FormatterBase

class Formatter(FormatterBase):

    def encode(self, value: Any, member_type: AnyType | None) -> Result[Primitives]:
        if isinstance(value, Sequence) and not is_homogenous_list(cast(Sequence[Any], value)):
            padding = len(str(len(cast(Sequence[Any], value))))
            return {
                f"{index:0{padding+1}}" : item
                for index, item in enumerate(cast(Sequence[Any], value))
            }, True
        else:
            return BaseFormatter.encode(value, member_type)


    def decode(self, value: Primitives, member_type: AnyType | None) -> Result[Any]:
        if isinstance(value, dict) and member_type and issubclass_typing(member_type, (list, tuple)):
            return list(cast(Mapping[str, Any], value).values()), True
        else:
            return BaseFormatter.decode(value, member_type)


def is_homogenous_list(value: Sequence[Any]) -> bool:
    last_type: AnyType | None = None
    for item in value:
        this_type = cast(AnyType, type(item))
        if last_type is not None and last_type != this_type:
            return False
        last_type = this_type
    return True
