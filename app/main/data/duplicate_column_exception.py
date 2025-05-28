class DuplicateColumnException(Exception):
    def __init__(self, table: str, values: dict[str, object]):
        super().__init__(f"Duplicate column(s) on {table}: {values.keys()}")
        self.table = table
        self.values = values
