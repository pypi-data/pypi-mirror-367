class ReadonlyException(Exception): # pragma: no cover
    def __init__(self, member: str):
        super().__init__(f"Member '{member}' is readonly")