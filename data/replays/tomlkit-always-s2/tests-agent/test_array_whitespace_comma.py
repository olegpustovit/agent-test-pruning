import pytest

from tomlkit import dumps
from tomlkit import parse


@pytest.mark.parametrize(
    "text",
    [
        "a = [1 , 2 ,3 ]",
        "a = [1 ,\n 2 , ]",
        "a = [ 1  ,  2  ,]",
        "a = [1  ,2   ,   3  ]\n",
        'a = ["x" , "y"]',
        "a = [1 , # c\n 2 ]",
    ],
)
def test_roundtrip_preserved(text):
    assert dumps(parse(text)) == text


def test_values_with_space_before_comma():
    doc = parse("a = [1 , 2 ,3 ]")
    assert doc["a"] == [1, 2, 3]


def test_no_adjacent_whitespace_only_groups():
    arr = parse("a = [1   , 2   , 3   ,  ]")["a"]
    groups = arr._value
    for prev, cur in zip(groups, groups[1:]):
        assert not (prev.value is None and cur.value is None)


def test_append_after_space_comma_array():
    doc = parse("a = [1 , 2 ]")
    doc["a"].append(3)
    assert doc["a"] == [1, 2, 3]
    assert parse(dumps(doc))["a"] == [1, 2, 3]
