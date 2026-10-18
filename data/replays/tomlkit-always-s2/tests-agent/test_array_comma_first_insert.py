import pytest

from tomlkit import dumps
from tomlkit import parse


ONE_COMMENT = "a = [\n  1\n  # c\n  ,2\n]\n"
TWO_COMMENTS = "a = [\n  1\n  # c\n  ,2\n  # d\n  ,3]\n"


@pytest.mark.parametrize(
    ("src", "pos", "expected", "values"),
    [
        (ONE_COMMENT, 1, "a = [\n  1\n  # c\n  ,99\n  ,2\n]\n", [1, 99, 2]),
        (ONE_COMMENT, 2, "a = [\n  1\n  # c\n  ,2\n  ,99\n]\n", [1, 2, 99]),
        (ONE_COMMENT, 3, "a = [\n  1\n  # c\n  ,2\n  ,99\n]\n", [1, 2, 99]),
        (
            TWO_COMMENTS,
            1,
            "a = [\n  1\n  # c\n  ,99\n  ,2\n  # d\n  ,3]\n",
            [1, 99, 2, 3],
        ),
        (
            TWO_COMMENTS,
            2,
            "a = [\n  1\n  # c\n  ,2\n  # d\n  ,99\n  ,3]\n",
            [1, 2, 99, 3],
        ),
        (
            TWO_COMMENTS,
            3,
            "a = [\n  1\n  # c\n  ,2\n  # d\n  ,3\n  ,99]\n",
            [1, 2, 3, 99],
        ),
    ],
)
def test_insert_into_comma_first_array_has_no_double_comma(
    src, pos, expected, values
):
    doc = parse(src)
    doc["a"].insert(pos, 99)
    out = dumps(doc)
    assert ",," not in out.replace(" ", "").replace("\n", "")
    assert out == expected
    assert list(parse(out)["a"]) == values


def test_append_into_comma_first_array_roundtrips():
    doc = parse(TWO_COMMENTS)
    doc["a"].append(99)
    out = dumps(doc)
    assert out == "a = [\n  1\n  # c\n  ,2\n  # d\n  ,3\n  ,99]\n"
    assert parse(out)["a"] == [1, 2, 3, 99]


def test_insert_at_start_keeps_trailing_comma():
    doc = parse(ONE_COMMENT)
    doc["a"].insert(0, 99)
    out = dumps(doc)
    assert out == "a = [\n  99,\n  1\n  # c\n  ,2\n]\n"
    assert parse(out)["a"] == [99, 1, 2]
