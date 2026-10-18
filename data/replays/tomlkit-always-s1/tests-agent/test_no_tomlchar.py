import importlib

import pytest

from tomlkit import loads
from tomlkit.exceptions import InvalidControlChar
from tomlkit.exceptions import ParseError
from tomlkit.exceptions import UnexpectedEofError
from tomlkit.source import Source


def test_toml_char_module_removed():
    with pytest.raises(ImportError):
        importlib.import_module("tomlkit.toml_char")


def test_source_yields_plain_str():
    src = Source("ab")
    assert type(src.current) is str
    assert src.current == "a"
    assert not src.end()
    src.inc()
    assert src.current == "b"
    assert not src.end()
    assert src.inc() is False
    assert src.end()


def test_empty_source_end():
    assert Source("").end()


def test_real_nul_in_source_not_eof():
    src = Source("a\0b")
    src.inc()
    assert src.current == "\0"
    assert not src.end()
    src.inc()
    assert src.current == "b"
    assert not src.end()
    src.inc()
    assert src.end()


@pytest.mark.parametrize(
    "doc",
    [
        'a = "x\0y"\n',
        "a = 'x\0y'\n",
        "a = 1 # c\0d\n",
        'a = """x\0y"""\n',
    ],
)
def test_nul_rejected_as_control_char(doc):
    with pytest.raises(InvalidControlChar):
        loads(doc)


@pytest.mark.parametrize("doc", ["a = \0", "\0", "a\0 = 1", "[a\0]\n"])
def test_nul_elsewhere_is_parse_error(doc):
    with pytest.raises(ParseError):
        loads(doc)


@pytest.mark.parametrize("doc", ['a = "abc', "a = 'abc", 'a = """abc', "a = [1,", "a ="])
def test_truncation_errors(doc):
    with pytest.raises(ParseError):
        loads(doc)


def test_unterminated_string_is_eof_error():
    with pytest.raises(UnexpectedEofError):
        loads('a = "abc')


def test_whitespace_and_comments_roundtrip():
    doc = "  a \t=\t 1 # c\r\n\r\n[t]\r\nb = [ 1 ,\n 2 ]\n# end"
    assert loads(doc).as_string() == doc
    assert loads("").as_string() == ""
    assert loads(" \t\n").as_string() == " \t\n"


def test_multiline_line_ending_backslash():
    assert loads('a = """x \\\n   \t y"""')["a"] == "x y"
