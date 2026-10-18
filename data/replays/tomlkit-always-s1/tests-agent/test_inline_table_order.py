from tomlkit import dumps
from tomlkit.items import AoT, item


def test_inline_table_preserves_order():
    v = item([[{"a": {"x": 1}, "b": 2}]])
    assert v.as_string() == "[[{a = {x = 1}, b = 2}]]"


def test_inline_table_sorted_alphabetically():
    v = item([1, {"b": 1, "a": {"x": 1}, "c": 3}], _sort_keys=True)
    assert v.as_string() == "[1, {a = {x = 1}, b = 1, c = 3}]"


def test_aot_dicts_last_default():
    v = item([{"a": {"x": 1}, "b": 2}])
    assert isinstance(v, AoT)
    assert list(v[0].keys()) == ["b", "a"]


def test_aot_sorted_dicts_last():
    v = item([{"z": 1, "b": {"x": 1}, "a": {"y": 1}, "c": 2}], _sort_keys=True)
    assert list(v[0].keys()) == ["z", "c", "a", "b"] or list(v[0].keys()) == ["c", "z", "a", "b"]
    assert list(v[0].keys())[-2:] == ["a", "b"]
