import pytest

from tomlkit import parse
from tomlkit.exceptions import ParseError
from tomlkit.exceptions import TOMLKitError


def test_table_redefined_after_parent_header_rejected():
    doc = "[a]\nx = 1\n[a.b]\ny = 1\n[a]\nz = 1\n"
    with pytest.raises(TOMLKitError):
        parse(doc)


def test_duplicate_nested_table_under_super_table_rejected():
    doc = "[a.b]\nx = 1\n[a.c]\ny = 1\n[a.b]\nz = 1\n"
    with pytest.raises(ParseError):
        parse(doc)


def test_duplicate_simple_table_rejected():
    with pytest.raises(ParseError):
        parse("[a]\nx = 1\n[a]\ny = 2\n")


def test_super_table_defined_later_is_valid():
    doc = parse("[a.b]\nx = 1\n[a]\ny = 2\n")
    assert doc == {"a": {"b": {"x": 1}, "y": 2}}


def test_distinct_subtables_valid():
    doc = parse("[a.b]\nx = 1\n[a.c]\ny = 2\n")
    assert doc == {"a": {"b": {"x": 1}, "c": {"y": 2}}}
