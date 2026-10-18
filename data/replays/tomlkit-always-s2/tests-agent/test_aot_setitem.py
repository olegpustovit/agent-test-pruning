import tomlkit

from tomlkit.items import AoT
from tomlkit.items import Table


def _doc():
    return tomlkit.parse('[[a]]\nx = 1\n\n[[a]]\nx = 2\n')


def test_aot_setitem_int():
    doc = _doc()
    doc["a"][0] = {"x": 10}
    assert isinstance(doc["a"], AoT)
    assert isinstance(doc["a"][0], Table)
    assert doc["a"][0]["x"] == 10
    assert doc["a"][1]["x"] == 2
    assert len(doc["a"]) == 2
    out = tomlkit.dumps(doc)
    assert tomlkit.parse(out) == {"a": [{"x": 10}, {"x": 2}]}


def test_aot_setitem_negative_index():
    doc = _doc()
    doc["a"][-1] = {"y": "z"}
    assert tomlkit.parse(tomlkit.dumps(doc)) == {"a": [{"x": 1}, {"y": "z"}]}

