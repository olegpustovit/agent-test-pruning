import pytest

from tomlkit import dumps
from tomlkit import loads
from tomlkit import string
from tomlkit.exceptions import InvalidStringError


def test_mlb_bare_cr_escaped_and_roundtrips():
    s = string('a\rb', multiline=True)
    out = s.as_string()
    assert "\r" not in out
    assert "\\r" in out
    assert loads("x = " + out)["x"] == "a\rb"


def test_mlb_crlf_not_escaped():
    s = string("a\r\nb", multiline=True)
    assert s.as_string() == '"""a\r\nb"""'


def test_mlb_trailing_cr_escaped():
    out = string("a\r", multiline=True).as_string()
    assert "\\r" in out
    assert loads("x = " + out)["x"] == "a\r"


def test_mll_bare_cr_rejected():
    with pytest.raises(InvalidStringError):
        string("a\rb", multiline=True, literal=True)


def test_mll_crlf_allowed():
    assert string("a\r\nb", multiline=True, literal=True).as_string() == "'''a\r\nb'''"
    assert string("a\nb", multiline=True, literal=True).as_string() == "'''a\nb'''"
