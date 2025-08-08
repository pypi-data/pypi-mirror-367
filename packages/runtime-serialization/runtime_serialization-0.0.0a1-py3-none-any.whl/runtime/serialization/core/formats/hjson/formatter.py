from typing import Any
from typingutils import AnyType

from runtime.serialization.core.helpers import Result
from runtime.serialization.core.primitives import Primitives
from runtime.serialization.core.base_formatter import BaseFormatter
from runtime.serialization.core.interfaces.formatter import Formatter as FormatterBase



class Formatter(FormatterBase):

    def encode(self, value: Any, member_type: AnyType | None) -> Result[Primitives]:
        return BaseFormatter.encode(value, member_type)

    def decode(self, value: Primitives, member_type: AnyType | None) -> Result[Any]:
        return BaseFormatter.decode(value, member_type)

