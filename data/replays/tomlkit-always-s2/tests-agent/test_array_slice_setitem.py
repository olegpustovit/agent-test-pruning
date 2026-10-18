import pytest

from tomlkit import dumps
from tomlkit import parse


def test_slice_assignment_raises_without_mutation():
    doc = parse("a = [1, 2, 3]\n")
    arr = doc["a"]
    with pytest.raises(ValueError, match="slice assignment is not supported"):
        arr[0:2] = [9, 9]
    assert list(arr) == [1, 2, 3]
    assert dumps(doc) == "a = [1, 2, 3]\n"


def test_slice_assignment_extended_slice_no_mutation():
    doc = parse("a = [1, 2, 3]\n")
    arr = doc["a"]
    with pytest.raises(ValueError):
        arr[::2] = [7, 8]
    assert list(arr) == [1, 2, 3]
    assert dumps(doc) == "a = [1, 2, 3]\n"


def test_index_assignment_still_works():
    doc = parse("a = [1, 2, 3]\n")
    doc["a"][-1] = 5
    doc["a"][0] = 4
    assert dumps(doc) == "a = [4, 2, 5]\n"
