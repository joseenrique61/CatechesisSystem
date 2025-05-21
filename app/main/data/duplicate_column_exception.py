class DuplicateColumnException(Exception):
    def __init__(self, table: str, columns: list[str]):
        super().__init__(f"Duplicate column on {table}: {columns}")
        self.table = table
        self.columns = columns
