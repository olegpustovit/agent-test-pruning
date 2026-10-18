import tomlkit

from tomlkit.items import AoT
from tomlkit.items import Table


def _doc():
    return tomlkit.parse("[[a]]\nx = 1\n\n[[a]]\nx = 2\n")


def test_aot_setitem_int():
    doc = _doc()
    aot = doc["a"]
    assert isinstance(aot, AoT)
    aot[0] = {"x": 10}
    assert isinstance(aot[0], Table)
    assert aot[0]["x"] == 10
    assert aot[1]["x"] == 2
    assert len(aot) == 2
    assert doc.unwrap() == {"a": [{"x": 10}, {"x": 2}]}


def test_aot_setitem_negative_index():
    doc = _doc()
    doc["a"][-1] = {"x": 5}
    assert doc.unwrap() == {"a": [{"x": 1}, {"x": 5}]}


def test_aot_setitem_out_of_range():
    import pytest

    doc = _doc()
    with pytest.raises(IndexError):
        doc["a"][5] = {"x": 1}
