import pytest

from tomlkit import parse
from tomlkit.exceptions import NonExistentKey
from tomlkit.items import Bool, Integer, String, Table


def test_array_item_returns_item_objects():
    doc = parse("a = [1, 'x', true]")
    arr = doc["a"]
    assert isinstance(arr.item(0), Integer)
    assert isinstance(arr.item(1), String)
    assert isinstance(arr.item(2), Bool)
    assert arr.item(-1) is arr.item(2)


def test_array_getitem_still_unwraps_bool():
    arr = parse("a = [true, false, 1]")["a"]
    assert isinstance(arr[0], Bool)
    assert arr[0] == True  # noqa: E712
    assert arr[1] == False  # noqa: E712
    assert arr[0].value is True
    assert arr[1].value is False
    assert arr[2] == 1


def test_array_item_out_of_range():
    arr = parse("a = [1]")["a"]
    with pytest.raises(IndexError):
        arr.item(5)


def test_table_item():
    doc = parse("[t]\nx = 1\nflag = true\n")
    t = doc["t"]
    assert isinstance(t, Table)
    assert isinstance(t.item("x"), Integer)
    assert isinstance(t.item("flag"), Bool)
    with pytest.raises(NonExistentKey):
        t.item("missing")


def test_document_item_returns_table():
    doc = parse("[t]\nx = 1\n")
    assert isinstance(doc.item("t"), Table)


def test_inline_table_item():
    t = parse("t = {a = 1}")["t"]
    assert isinstance(t.item("a"), Integer)
