import tomlkit

from tomlkit import dumps
from tomlkit import parse


DOC = "b = 1\na = 2\n\n[z]\ny = 1\nx = 2\n\n[c]\nk = 1\n"


def test_parsed_document_sort_keys():
    out = dumps(parse(DOC), sort_keys=True)
    assert out.index("a = 2") < out.index("b = 1")
    assert out.index("[c]") < out.index("[z]")
    assert tomlkit.parse(out) == tomlkit.parse(DOC)


def test_parsed_document_unsorted_preserves_formatting():
    assert dumps(parse(DOC)) == DOC
    assert dumps(parse(DOC), sort_keys=False) == DOC


def test_parsed_table_sort_keys_keeps_content():
    doc = parse(DOC)
    out = dumps(doc["z"], sort_keys=True)
    assert "x = 2" in out
    assert "y = 1" in out


def test_plain_dict_sort_keys():
    assert dumps({"b": 1, "a": 2}, sort_keys=True) == "a = 2\nb = 1\n"
