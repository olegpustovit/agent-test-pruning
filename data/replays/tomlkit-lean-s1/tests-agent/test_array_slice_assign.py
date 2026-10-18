import pytest

from tomlkit import array


def test_slice_assignment_rejected_without_mutation():
    a = array("[1, 2, 3]")
    with pytest.raises(ValueError, match="slice assignment is not supported"):
        a[0:2] = [9]
    assert list(a) == [1, 2, 3]
    assert a.as_string() == "[1, 2, 3]"
