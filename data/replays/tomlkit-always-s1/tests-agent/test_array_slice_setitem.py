import pytest

from tomlkit import array
from tomlkit import dumps
from tomlkit import parse


def test_slice_assignment_raises_and_does_not_mutate():
    a = array("[1, 2, 3]")
    with pytest.raises(ValueError, match="slice assignment is not supported"):
        a[0:2] = [9, 9]
    assert list(a) == [1, 2, 3]
    assert a.as_string() == "[1, 2, 3]"


def test_slice_assignment_in_document_does_not_mutate():
    doc = parse("a = [1, 2, 3]\n")
    with pytest.raises(ValueError):
        doc["a"][:] = [7]
    assert doc["a"] == [1, 2, 3]
    assert dumps(doc) == "a = [1, 2, 3]\n"


def test_index_assignment_still_works():
    a = array("[1, 2, 3]")
    a[1] = 5
    a[-1] = 6
    assert a.as_string() == "[1, 5, 6]"
