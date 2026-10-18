import pytest

import tomlkit


def _arr(s="[1, 2, 3, 4, 5]"):
    return tomlkit.parse(f"a = {s}")["a"]


@pytest.mark.parametrize(
    "key",
    [
        slice(None, None, -1),
        slice(None, 2),
        slice(2, None),
        slice(-2, None),
        slice(None, -1),
        slice(None, None, 2),
        slice(1, None, 2),
        slice(-1, None, -2),
        slice(10, 20),
        slice(0, 0),
        slice(None),
    ],
)
def test_slice_delete_matches_list(key):
    arr = _arr()
    expected = [1, 2, 3, 4, 5]
    del expected[key]
    del arr[key]
    assert arr == expected
    doc = tomlkit.parse(f"a = {arr.as_string()}")
    assert doc["a"] == expected


def test_slice_delete_negative_start_rendering():
    doc = tomlkit.parse("a = [1, 2, 3, 4, 5]")
    del doc["a"][-2:]
    assert doc.as_string() == "a = [1, 2, 3]"


def test_slice_delete_reverse_rendering():
    doc = tomlkit.parse("a = [1, 2, 3]")
    del doc["a"][::-1]
    assert doc["a"] == []
    assert tomlkit.parse(doc.as_string())["a"] == []
