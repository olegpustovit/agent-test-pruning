import pytest

import tomlkit

from tomlkit.items import Item


def test_item_base_has_no_indexing():
    for name in ("__getitem__", "__setitem__", "__delitem__"):
        assert name not in vars(Item)


@pytest.mark.parametrize("value", [1, 1.5, True, 1.5e3])
def test_scalar_not_subscriptable(value):
    it = tomlkit.item(value)
    with pytest.raises(TypeError):
        it[0]
    with pytest.raises(TypeError):
        it[0] = 1
    with pytest.raises(TypeError):
        del it[0]


def test_float_not_a_sequence():
    from collections.abc import Sequence

    assert not isinstance(tomlkit.item(1.5), Sequence)


def test_string_indexing_and_tables_still_work():
    assert tomlkit.item("abc")[1] == "b"
    t = tomlkit.parse("a = 1\n")
    t["b"] = 2
    assert t["b"] == 2
    del t["b"]
    assert "b" not in t
    with pytest.raises(TypeError):
        tomlkit.item("abc")[0] = "x"
