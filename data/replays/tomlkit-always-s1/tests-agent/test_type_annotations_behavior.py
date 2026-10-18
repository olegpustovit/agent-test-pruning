from __future__ import annotations

import pytest

import tomlkit

from tomlkit._utils import merge_dicts
from tomlkit.container import Container
from tomlkit.items import DottedKey


def test_dumps_plain_mapping_and_sort_keys():
    assert tomlkit.dumps({"b": 1, "a": 2}, sort_keys=True) == "a = 2\nb = 1\n"
    assert tomlkit.dumps({"a": {"x": 1}}) == "[a]\nx = 1\n"


def test_dumps_container_and_document():
    doc = tomlkit.parse("a = 1  # c\n")
    assert tomlkit.dumps(doc) == "a = 1  # c\n"
    assert tomlkit.dumps(doc.value if False else doc.unwrap()) == "a = 1\n"


def test_array_returns_array_and_rejects_non_array():
    a = tomlkit.array("[1, 2]")
    assert isinstance(a, tomlkit.items.Array)
    assert a == [1, 2]
    with pytest.raises(ValueError):
        tomlkit.array("1")


def test_key_iterable_builds_dotted_key():
    k = tomlkit.key(["a", "b"])
    assert isinstance(k, DottedKey)
    assert k.as_string() == "a.b"


def test_merge_dicts_in_place_returns_none():
    d1 = {"a": {"x": 1}, "b": 1}
    assert merge_dicts(d1, {"a": {"y": 2}, "b": 3}) is None
    assert d1 == {"a": {"x": 1, "y": 2}, "b": 3}


def test_container_setdefault():
    c = Container()
    assert c.setdefault("a", 1) == 1
    assert c.setdefault("a", 2) == 1


def test_out_of_order_proxy_setdefault_and_delete():
    doc = tomlkit.parse("[a.b]\nx=1\n[c]\ny=1\n[a.d]\nz=1\n")
    proxy = doc["a"]
    assert proxy.setdefault("b", None)["x"] == 1
    proxy.setdefault("e", 5)
    assert proxy["e"] == 5
    del proxy["b"]
    assert "b" not in proxy


def test_container_add_comment_and_unwrap_dotted():
    doc = tomlkit.document()
    doc.add(tomlkit.comment("hi"))
    doc.add("a", 1)
    assert doc.as_string() == "# hi\na = 1\n"
    merged = tomlkit.parse("[a.b]\nx=1\n[c]\n[a.d]\nz=1\n").unwrap()
    assert merged == {"a": {"b": {"x": 1}, "d": {"z": 1}}, "c": {}}


def test_container_last_item_empty_and_eq():
    c = Container()
    assert c._previous_item() is None
    assert Container() == {}
    assert (Container() == 1) is False
