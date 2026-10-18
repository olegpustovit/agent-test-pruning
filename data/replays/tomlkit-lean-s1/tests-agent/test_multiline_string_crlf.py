import pytest

from tomlkit import parse
from tomlkit.exceptions import UnexpectedEofError


def test_multiline_basic_string_crlf():
    doc = parse('a = """x\r\ny\r\nz"""\r\n')
    assert doc["a"] == "x\ny\nz" or doc["a"] == "x\r\ny\r\nz"
    assert doc.as_string() == 'a = """x\r\ny\r\nz"""\r\n'


def test_multiline_literal_string_crlf():
    doc = parse("a = '''x\r\ny'''")
    assert "y" in doc["a"]
    assert doc.as_string() == "a = '''x\r\ny'''"


def test_multiline_string_ends_after_crlf_raises():
    with pytest.raises(UnexpectedEofError):
        parse('a = """x\r\n')
