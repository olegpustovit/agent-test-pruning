from tomlkit import loads
from tomlkit import parse


def _check(doc, expected):
    text = doc.as_string()
    assert text == expected
    assert loads(text) == doc


def test_dotted_key_replaced_by_table_no_duplicate_prefix():
    doc = parse("a.b = 1\n")
    doc["a"] = {"x": 1}
    _check(doc, "[a]\nx = 1\n")


def test_dotted_key_replaced_by_table_does_not_capture_sibling():
    doc = parse("a.b = 1\nc = 2\n")
    doc["a"] = {"x": 1}
    _check(doc, "c = 2\n\n[a]\nx = 1\n")


def test_value_replaced_by_table_before_dotted_key():
    doc = parse("x = 1\na.b = 1\n")
    doc["x"] = {"y": 1}
    _check(doc, "a.b = 1\n\n[x]\ny = 1\n")


def test_dotted_key_replaced_by_aot_does_not_capture_dotted_sibling():
    from tomlkit import aot
    from tomlkit import table

    doc = parse("a.b = 1\nc.d = 2\n")
    t = table()
    t["x"] = 1
    arr = aot()
    arr.append(t)
    doc["a"] = arr
    text = doc.as_string()
    assert text.index("c.d = 2") < text.index("[[a]]")
    back = loads(text)
    assert back == doc
    assert back["c"] == {"d": 2}
    assert back["a"] == [{"x": 1}]
