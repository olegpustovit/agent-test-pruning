from collections.abc import Sequence

import pytest

import tomlkit

from tomlkit.items import Item


DOC = 'f = 1.5\ni = 1\nd = 1979-05-27\nt = 07:32:00\ndt = 1979-05-27T07:32:00\ns = "abc"\n'


def test_item_base_has_no_item_access():
    for name in ("__getitem__", "__setitem__", "__delitem__"):
        assert name not in vars(Item)


@pytest.mark.parametrize("key", ["f", "i", "d", "t", "dt"])
def test_scalars_not_sequences_or_subscriptable(key):
    v = tomlkit.parse(DOC)[key]
    assert not isinstance(v, Sequence)
    assert not hasattr(v, "__getitem__")
    with pytest.raises(TypeError):
        v[0]
    with pytest.raises(TypeError):
        v[0] = 1
    with pytest.raises(TypeError):
        del v[0]


def test_string_still_indexable():
    s = tomlkit.parse(DOC)["s"]
    assert s[0] == "a"
    assert s[1:] == "bc"


def test_containers_still_work():
    doc = tomlkit.parse("a = [1, 2]\n[t]\nx = 1\n")
    assert doc["a"][1] == 2
    doc["t"]["y"] = 2
    del doc["t"]["x"]
    assert dict(doc["t"]) == {"y": 2}
    doc["a"][0] = 5
    assert doc["a"][0] == 5
