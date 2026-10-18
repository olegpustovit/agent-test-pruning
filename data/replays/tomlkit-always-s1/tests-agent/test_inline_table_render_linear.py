import pytest

import tomlkit

from tomlkit.items import InlineTable


def test_large_inline_table_roundtrip():
    src = "t = {" + ", ".join(f"k{i} = {i}" for i in range(500)) + "}\n"
    doc = tomlkit.parse(src)
    assert doc.as_string() == src
    assert len(doc["t"]) == 500


def test_large_inline_table_delete_last_keys():
    n = 50
    doc = tomlkit.parse("t = {" + ", ".join(f"k{i} = {i}" for i in range(n)) + "}\n")
    del doc["t"]["k49"]
    del doc["t"]["k48"]
    out = doc.as_string()
    assert tomlkit.parse(out)["t"] == {f"k{i}": i for i in range(48)}
    assert ", }" not in out and ",}" not in out


@pytest.mark.parametrize("victim", ["a", "b", "c"])
def test_delete_each_key(victim):
    doc = tomlkit.parse("t = {a = 1, b = 2, c = 3}\n")
    del doc["t"][victim]
    expected = {k: v for k, v in dict(a=1, b=2, c=3).items() if k != victim}
    out = doc.as_string()
    assert tomlkit.parse(out)["t"] == expected
    assert ",," not in out.replace(" ", "")


def test_delete_all_keys():
    doc = tomlkit.parse("t = {a = 1, b = 2}\n")
    del doc["t"]["a"]
    del doc["t"]["b"]
    assert tomlkit.parse(doc.as_string())["t"] == {}


def test_delete_then_add():
    doc = tomlkit.parse("t = {a = 1, b = 2, c = 3}\n")
    del doc["t"]["c"]
    doc["t"]["d"] = 4
    assert tomlkit.parse(doc.as_string())["t"] == {"a": 1, "b": 2, "d": 4}


def test_trailing_comma_preserved_when_nothing_deleted():
    src = "t = {a = 1, b = 2,}\n"
    assert tomlkit.parse(src).as_string() == src


def test_new_inline_table():
    t = tomlkit.inline_table()
    for i in range(20):
        t[f"k{i}"] = i
    assert isinstance(t, InlineTable)
    assert tomlkit.parse(f"x = {t.as_string()}")["x"] == {f"k{i}": i for i in range(20)}
    del t["k19"]
    assert tomlkit.parse(f"x = {t.as_string()}")["x"] == {f"k{i}": i for i in range(19)}
