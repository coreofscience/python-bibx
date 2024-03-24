from bibx._fuzz.distance import distance


def test_distance():
    assert distance("abc", "abc") == 0


def test_distance_substring():
    assert distance("abc", "abcxy") == 0
    assert distance("abcxy", "abc") == 0


def test_distance_different():
    assert distance("abc", "abrxy") == 1
    assert distance("abcxy", "abr") == 1


def test_distance_with_empty_string():
    assert distance("", "abc") == 0
    assert distance("abc", "") == 0


def test_distance_matching_at_the_end():
    assert distance("abc", "xyabc") == 0
    assert distance("xyabc", "abc") == 0
