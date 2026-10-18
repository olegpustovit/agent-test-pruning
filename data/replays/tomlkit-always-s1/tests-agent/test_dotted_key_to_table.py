from tomlkit import loads
from tomlkit import parse


def test_dotted_key_replaced_by_table_no_duplicate_prefix():
    doc = parse("a.b = 1\n")
    doc["a"] = {"x": 1}
    out = doc.as_string()
    assert "a.a" not in out and "a.[" not in out
    assert loads(out) == {"a": {"x": 1}}


def test_dotted_key_replaced_by_table_does_not_capture_sibling():
    doc = parse("a.b = 1\nc = 2\n")
    doc["a"] = {"x": 1}
    out = doc.as_string()
    assert out == "c = 2\n\n[a]\nx = 1\n"
    assert loads(out) == {"c": 2, "a": {"x": 1}}


def test_dotted_key_replaced_by_table_before_other_dotted_key():
    doc = parse("a.b = 1\nc.d = 2\n")
    doc["a"] = {"x": 1}
    assert loads(doc.as_string()) == {"c": {"d": 2}, "a": {"x": 1}}


def test_dotted_key_replaced_stays_before_real_header():
    doc = parse("a.b = 1\n[t]\ny = 1\n")
    doc["a"] = {"x": 1}
    assert loads(doc.as_string()) == {"a": {"x": 1}, "t": {"y": 1}}


def test_value_replaced_by_table_before_dotted_key():
    doc = parse("x = 1\na.b = 1\n[t]\ny = 1\n")
    doc["x"] = {"q": 1}
    out = doc.as_string()
    assert out.index("a.b = 1") < out.index("[x]")
    assert loads(out) == {"a": {"b": 1}, "x": {"q": 1}, "t": {"y": 1}}
