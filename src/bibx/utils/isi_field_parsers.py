from typing import List


def joined(values: List[str], separator: str = " ") -> str:
    return separator.join(value.strip() for value in values)


def ident(values: List[str]) -> List[str]:
    return [value.strip() for value in values]


def delimited(values: List[str], delimiter: str = "; ") -> List[str]:
    return [
        word.replace(delimiter.strip(), "")
        for words in values
        for word in words.split(delimiter)
        if word
    ]


def integer(values: List[str]) -> int:
    if len(values) > 1:
        raise ValueError(f"Expected no more than one item and got {len(values)}")

    first, *_ = values
    return int(first.strip())
