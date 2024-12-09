class Worksheet:
    # NOTE: In reality, the write method has many overloads.
    def write(
        self,
        row: int,
        col: int,
        value: int | float | str | None,
    ) -> None: ...
