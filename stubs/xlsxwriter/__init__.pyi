from xlsxwriter.worksheet import Worksheet

class Workbook:
    def __init__(self, filename: str) -> None: ...
    def add_worksheet(self, title: str) -> Worksheet: ...
    def close(self) -> None: ...
