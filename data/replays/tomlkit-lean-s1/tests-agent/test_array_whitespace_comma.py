import pytest

import tomlkit


@pytest.mark.parametrize(
    "text",
    [
        "a = [1 , 2 ,3]",
        "a = [1  ,\n 2]",
        "a = [ 1 ,]",
        "a = [1,2 , ]",
    ],
)
def test_space_before_comma_roundtrip(text):
    doc = tomlkit.parse(text)
    assert doc.as_string() == text


def test_space_before_comma_merged_with_comma():
    arr = tomlkit.parse("a = [1 , 2]")["a"]
    assert arr._value[0].comma.s == " ,"
    assert arr == [1, 2]


def test_space_before_comma_edit():
    doc = tomlkit.parse("a = [1 , 2 ,3]")
    del doc["a"][0]
    assert doc["a"] == [2, 3]
    doc["a"].append(9)
    assert doc["a"] == [2, 3, 9]
    assert tomlkit.parse(doc.as_string())["a"] == [2, 3, 9]
