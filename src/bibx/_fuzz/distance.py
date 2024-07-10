from Levenshtein import distance as _levenshtein_distance

from bibx._fuzz.utils import normalize


def distance(a: str, b: str) -> int:
    """Compute the distance between two strings.

    The distance should be zero if one of the strings contain the other.
    """
    a = normalize(a)
    b = normalize(b)
    shorter, longer = (a, b) if len(a) < len(b) else (b, a)
    if shorter in longer:
        return 0
    if shorter == "":
        return 0
    _len_shorter = len(shorter)
    _len_longer = len(longer)
    min_distance = _levenshtein_distance(shorter, longer[:_len_shorter])
    for i in range(_len_longer - _len_shorter):
        distance = _levenshtein_distance(shorter, longer[i : i + _len_shorter])
        if distance < min_distance:
            min_distance = distance
    return min_distance
