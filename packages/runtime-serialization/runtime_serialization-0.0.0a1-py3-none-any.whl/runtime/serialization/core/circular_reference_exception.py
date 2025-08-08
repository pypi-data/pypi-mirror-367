from typingutils import get_type_name

class CircularReferenceException(Exception):
    def __init__(self, type1: type, type2: type, path: str):
        super().__init__(f"A circular dependency between '{get_type_name(type1)}' and '{get_type_name(type2)}' has been discovered on path {path}")
