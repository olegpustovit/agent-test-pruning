import tomlkit

from tomlkit import dumps
from tomlkit import parse


def test_sort_keys_parsed_document():
    doc = parse("b = 1\na = 2\n[z]\ny = 1\nx = 2\n[c]\nk = 1\n")
    out = dumps(doc, sort_keys=True)
    assert out.index("a = 2") < out.index("b = 1")
    assert out.index("[c]") < out.index("[z]")
    assert parse(out) == doc


def test_no_sort_preserves_original():
    src = "b = 1\na = 2\n# comment\n[z]\ny = 1\nx = 2\n"
    assert dumps(parse(src)) == src
    assert dumps(parse(src), sort_keys=False) == src


def test_sort_keys_table_does_not_mutate():
    doc = parse("[t]\nb = 1\na = 2\n")
    out = dumps(doc["t"], sort_keys=True)
    assert parse(out) == {"b": 1, "a": 2}
    assert doc.as_string() == "[t]\nb = 1\na = 2\n"


def test_sort_keys_plain_dict():
    out = dumps({"b": 1, "a": 2}, sort_keys=True)
    assert out == "a = 2\nb = 1\n"


def test_sort_keys_created_document():
    doc = tomlkit.document()
    doc["b"] = 1
    doc["a"] = 2
    assert dumps(doc, sort_keys=True) == "a = 2\nb = 1\n"
