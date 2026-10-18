import tomlkit
import tomlkit._types as types

from tomlkit.items import Array
from tomlkit.items import Table


def test_wrap_method_removed():
    assert not hasattr(types, "wrap_method")
    assert "wrap_method" not in types.__all__


def test_array_add():
    doc = tomlkit.parse("a = [1, 2]")
    result = doc["a"] + [3, 4]
    assert list(result) == [1, 2, 3, 4]
    assert list(doc["a"]) == [1, 2]


def test_array_iadd():
    doc = tomlkit.parse("a = [1, 2]")
    arr = doc["a"]
    original = arr
    arr += [3]
    assert arr is original
    assert isinstance(arr, Array)
    assert list(doc["a"]) == [1, 2, 3]


def test_table_or_preserves_original():
    t = tomlkit.table()
    t["a"] = 1
    result = t | {"b": 2}
    assert isinstance(result, Table)
    assert result["a"] == 1
    assert result["b"] == 2
    assert "b" not in t


def test_table_ior_in_place():
    t = tomlkit.table()
    t["a"] = 1
    original = t
    t |= {"b": 2}
    assert t is original
    assert t["b"] == 2
