from enum import Enum

class DeserializationStrategy(Enum):
    CONSTRUCTOR = 0
    FIELDS = 1
    FIELDS_OR_PROPERTIES = 2
