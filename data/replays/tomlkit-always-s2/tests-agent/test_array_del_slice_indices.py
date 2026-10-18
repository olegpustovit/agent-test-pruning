import pytest

import tomlkit


def _arr(src="a = [1, 2, 3, 4, 5]"):
    return tomlkit.parse(src)["a"]


@pytest.mark.parametrize(
    "sl",
    [
        slice(None, 2),
        slice(2, None),
        slice(-2, None),
        slice(None, -1),
        slice(None, None, 2),
        slice(None, None, -1),
        slice(1, 100),
        slice(-100, 2),
        slice(3, 1, -1),
        slice(-1, None, -2),
        slice(4, 2),
    ],
)
def test_del_slice_matches_list(sl):
    doc = tomlkit.parse("a = [1, 2, 3, 4, 5]")
    expected = [1, 2, 3, 4, 5]
    del expected[sl]
    del doc["a"][sl]
    assert doc["a"] == expected
    reparsed = tomlkit.parse(doc.as_string())
    assert reparsed["a"] == expected


def test_del_negative_start_slice_renders():
    doc = tomlkit.parse("a = [1, 2, 3, 4, 5]")
    del doc["a"][-2:]
    assert doc.as_string() == "a = [1, 2, 3]"


def test_del_stop_zero_slice_noop():
    doc = tomlkit.parse("a = [1, 2, 3]")
    del doc["a"][:0]
    assert doc.as_string() == "a = [1, 2, 3]"
