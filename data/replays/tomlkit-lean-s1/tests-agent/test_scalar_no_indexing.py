import collections.abc as abc

import pytest

from tomlkit import item


@pytest.mark.parametrize("value", [1.5, 1, True])
def test_numeric_and_bool_items_are_not_subscriptable(value):
    it = item(value)
    assert not hasattr(it, "__getitem__")
    assert not isinstance(it, abc.Sequence)
    with pytest.raises(TypeError):
        it[0]
    with pytest.raises(TypeError):
        it[0] = 1
    with pytest.raises(TypeError):
        del it[0]


def test_string_item_still_indexable():
    assert item("abc")[1] == "b"
