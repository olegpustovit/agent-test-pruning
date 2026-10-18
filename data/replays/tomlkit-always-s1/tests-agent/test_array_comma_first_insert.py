import pytest

from tomlkit import dumps
from tomlkit import parse


COMMA_FIRST = "a = [\n  1\n  # c\n  , 2\n  # d\n  , 3\n]\n"


def _roundtrip(doc):
    out = dumps(doc)
    return out, parse(out)["a"]


def test_append_to_comma_first_array_with_comments():
    doc = parse(COMMA_FIRST)
    doc["a"].append(99)
    out, arr = _roundtrip(doc)
    assert ",," not in out.replace(" ", "")
    assert arr == [1, 2, 3, 99]


@pytest.mark.parametrize(
    "src,pos,expected",
    [
        (COMMA_FIRST, 0, [99, 1, 2, 3]),
        ("a = [\n    1\n    , 2\n    # c\n    , 3\n]\n", 1, [1, 99, 2, 3]),
        ("a = [\n  1,\n  2\n  # c\n  , 3\n]\n", 1, [1, 99, 2, 3]),
    ],
)
def test_insert_into_comma_first_array_stays_valid(src, pos, expected):
    doc = parse(src)
    doc["a"].insert(pos, 99)
    out, arr = _roundtrip(doc)
    assert arr == expected
    assert ",," not in out.replace(" ", "")


def test_insert_at_end_of_comma_first_array():
    doc = parse(COMMA_FIRST)
    doc["a"].insert(3, 99)
    _, arr = _roundtrip(doc)
    assert arr == [1, 2, 3, 99]
