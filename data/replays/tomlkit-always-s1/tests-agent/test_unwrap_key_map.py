import pytest

from tomlkit import loads
from tomlkit.exceptions import KeyAlreadyPresent
from tomlkit.items import Table


DOC = """\
a = 1
d.e.f = 3
inline = {p = 1, q = {r = 2}}
[t]
x = 1
[t.sub]
y = [1, 2]
[[aot]]
n = 1
[[aot]]
n = 2
"""


def test_unwrap_plain_values_and_order():
    doc = loads(DOC)
    out = doc.unwrap()
    assert out == {
        "a": 1,
        "t": {"x": 1, "sub": {"y": [1, 2]}},
        "aot": [{"n": 1}, {"n": 2}],
        "d": {"e": {"f": 3}},
        "inline": {"p": 1, "q": {"r": 2}},
    }
    assert list(out) == ["a", "d", "inline", "t", "aot"]
    assert type(out["t"]) is dict
    assert type(out["aot"][0]) is dict


def test_table_unwrap_delegates_to_container():
    doc = loads(DOC)
    t = doc["t"]
    assert isinstance(t, Table)
    assert t.unwrap() == {"x": 1, "sub": {"y": [1, 2]}}
    assert type(t.unwrap()["sub"]) is dict


def test_unwrap_out_of_order_tables_merged():
    doc = loads("[a.b]\nx = 1\n[c]\nz = 3\n[a.d]\ny = 2\n")
    assert doc.unwrap() == {"a": {"b": {"x": 1}, "d": {"y": 2}}, "c": {"z": 3}}
    assert list(doc.unwrap()) == ["a", "c"]


def test_unwrap_out_of_order_dotted_keys():
    doc = loads("a.b = 1\nc = 2\na.d = 3\n")
    assert doc.unwrap() == {"a": {"b": 1, "d": 3}, "c": 2}


def test_unwrap_after_delete_and_set():
    doc = loads("a = 1\nb = 2\n[t]\nx = 1\n")
    del doc["a"]
    doc["c"] = 3
    doc["t"]["y"] = 2
    out = doc.unwrap()
    assert out == {"b": 2, "t": {"x": 1, "y": 2}, "c": 3}
    # c is a bare key, emitted before the [t] table in dumps()
    assert list(out) == ["b", "c", "t"]


def test_unwrap_quoted_keys_use_bare_key_string():
    doc = loads('"a b" = 1\n[ "x.y" ]\n"k" = 2\n')
    assert doc.unwrap() == {"a b": 1, "x.y": {"k": 2}}


def test_unwrap_empty():
    assert loads("").unwrap() == {}
    assert loads("[t]\n").unwrap() == {"t": {}}


def test_unwrap_conflicting_out_of_order_raises():
    # Same behaviour as before: a conflicting fragment surfaces from unwrap().
    try:
        doc = loads("[a.b]\nx = 1\n[c]\nz = 3\n[a.b]\nx = 2\n")
    except Exception:
        return  # rejected at parse time
    with pytest.raises(KeyAlreadyPresent):
        doc.unwrap()
