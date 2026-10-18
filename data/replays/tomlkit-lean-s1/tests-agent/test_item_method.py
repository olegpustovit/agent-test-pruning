import pytest

from tomlkit import parse
from tomlkit.exceptions import NonExistentKey
from tomlkit.items import Bool
from tomlkit.items import Integer
from tomlkit.items import String


def test_array_item_returns_item_objects():
    doc = parse("a = [1, true, 'x']")
    arr = doc["a"]
    assert isinstance(arr.item(0), Integer)
    assert isinstance(arr.item(1), Bool)
    assert isinstance(arr.item(2), String)
    assert arr.item(-1) is arr.item(2)


def test_array_getitem_bool_values():
    arr = parse("a = [true, false, 1]")["a"]
    assert arr[0] == True  # noqa: E712
    assert arr[1] == False  # noqa: E712
    assert isinstance(arr[2], Integer)


def test_array_item_out_of_range():
    with pytest.raises(IndexError):
        parse("a = [1]")["a"].item(5)


def test_table_item_returns_item_object():
    doc = parse("[t]\nflag = true\nn = 1\n")
    t = doc["t"]
    assert isinstance(t.item("flag"), Bool)
    assert isinstance(t.item("n"), Integer)
    assert t["flag"] is True
    with pytest.raises(NonExistentKey):
        t.item("missing")


def test_inline_table_item():
    t = parse("t = {flag = true}")["t"]
    assert isinstance(t.item("flag"), Bool)
