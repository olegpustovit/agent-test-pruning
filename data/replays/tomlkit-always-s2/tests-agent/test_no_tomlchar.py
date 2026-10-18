import importlib

import pytest

import tomlkit

from tomlkit.exceptions import InvalidControlChar
from tomlkit.exceptions import UnexpectedEofError
from tomlkit.exceptions import ParseError
from tomlkit.source import Source


def test_toml_char_module_removed():
    with pytest.raises(ImportError):
        importlib.import_module("tomlkit.toml_char")


def test_source_yields_plain_str():
    s = Source("ab")
    assert type(s.current) is str
    assert s.current == "a"
    assert not s.end()
    s.inc()
    assert s.current == "b"
    assert not s.end()
    s.inc()
    assert s.end()
    assert s.current == "\0"


def test_source_end_empty():
    assert Source("").end()


def test_source_end_positional_with_real_nul():
    s = Source("\0")
    assert s.current == "\0"
    assert not s.end()
    s.inc()
    assert s.end()


@pytest.mark.parametrize(
    "doc",
    ['a = "x\0y"', "a = 'x\0y'", "# c\0\n", 'a = """x\0"""', "a = 1\0", "\0"],
)
def test_real_nul_rejected(doc):
    with pytest.raises(ParseError):
        tomlkit.parse(doc)


def test_nul_in_string_is_invalid_control_char():
    with pytest.raises(InvalidControlChar):
        tomlkit.parse('a = "x\0y"')


@pytest.mark.parametrize("doc", ['a = "abc', "a = 'abc", 'a = """abc', 'a = "abc\\'])
def test_unterminated_string_eof(doc):
    with pytest.raises(UnexpectedEofError):
        tomlkit.parse(doc)


@pytest.mark.parametrize("doc", ["", "   ", "\n", "\r\n", "# only comment", "a = 1"])
def test_roundtrip_edges(doc):
    assert tomlkit.parse(doc).as_string() == doc


def test_char_classes_roundtrip():
    doc = 'a \t=\t 1 # c\r\nb = [ 1,\n\t2 ]\nc = """x \\\n   y"""\nd = {x = 1}\n'
    assert tomlkit.parse(doc).as_string() == doc
    assert tomlkit.parse(doc)["c"] == "x y"
