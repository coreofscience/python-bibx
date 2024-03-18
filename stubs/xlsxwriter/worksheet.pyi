from typing import Union

class Worksheet:
    # NOTE: In reality, the write method has many overloads.
    def write(
        self,
        row: int,
        col: int,
        value: Union[int, float, str, None],
    ) -> None: ...
