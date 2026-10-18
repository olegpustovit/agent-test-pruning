import pytest

from tomlkit import loads
from tomlkit.exceptions import ParseError


def test_table_redefined_after_parent_header_rejected():
    doc = "[a.b]\nx = 1\n[a]\ny = 2\n[a.b]\nz = 3\n"
    with pytest.raises(ParseError, match="already exists"):
        loads(doc)


def test_duplicate_table_rejected():
    with pytest.raises(ParseError, match="already exists"):
        loads("[a]\nx = 1\n[a]\ny = 2\n")


def test_nested_duplicate_under_super_table_rejected():
    with pytest.raises(ParseError):
        loads("[a.b.c]\nx = 1\n[a.b.c]\ny = 2\n")


def test_valid_super_table_then_header_allowed():
    doc = "[a.b]\nx = 1\n[a]\ny = 2\n"
    parsed = loads(doc)
    assert parsed["a"]["b"]["x"] == 1
    assert parsed["a"]["y"] == 2
    assert parsed.as_string() == doc


def test_sibling_subtables_allowed():
    doc = "[a.b]\nx = 1\n[a.c]\ny = 2\n[a]\nz = 3\n"
    parsed = loads(doc)
    assert parsed["a"]["c"]["y"] == 2
    assert parsed["a"]["z"] == 3
