from __future__ import annotations
from collections.abc import Mapping, Sequence
from types import NoneType

Primitive = NoneType | bool | int | float | str
PrimitiveMapping = Mapping[str, 'Primitive | PrimitiveSequence | PrimitiveMapping']
PrimitiveSequence = Sequence['Primitive | PrimitiveSequence | PrimitiveMapping']
Primitives = Primitive | PrimitiveMapping | PrimitiveSequence