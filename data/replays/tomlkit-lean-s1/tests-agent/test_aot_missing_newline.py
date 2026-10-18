from tomlkit import aot
from tomlkit import loads
from tomlkit import parse


def test_aot_added_after_table_without_trailing_newline():
    doc = parse("[t]\nx=1")
    doc["u"] = aot()
    doc["u"].append({"q": 1})
    out = doc.as_string()
    assert out == "[t]\nx=1\n[[u]]\nq = 1\n"
    assert loads(out) == {"t": {"x": 1}, "u": [{"q": 1}]}


def test_nested_aot_added_after_table_without_trailing_newline():
    doc = parse("[t]\nx=1")
    doc["t"]["a"] = aot()
    doc["t"]["a"].append({"q": 1})
    out = doc.as_string()
    assert out == "[t]\nx=1\n[[t.a]]\nq = 1\n"
    assert loads(out) == {"t": {"x": 1, "a": [{"q": 1}]}}
