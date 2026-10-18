import pytest

from tomlkit.exceptions import InvalidStringError
from tomlkit.items import String
from tomlkit.items import StringType
from tomlkit import parse, dumps, item


def test_mlb_escapes_bare_cr():
    s = String.from_raw("a\rb", StringType.MLB)
    assert s.as_string() == '"""a\\rb"""'


def test_mlb_escapes_trailing_cr():
    assert String.from_raw("a\r", StringType.MLB).as_string() == '"""a\\r"""'


def test_mlb_keeps_crlf():
    assert String.from_raw("a\r\nb", StringType.MLB).as_string() == '"""a\r\nb"""'


def test_mlb_mixed_crlf_and_bare_cr():
    s = String.from_raw("a\r\nb\rc", StringType.MLB)
    assert s.as_string() == '"""a\r\nb\\rc"""'


@pytest.mark.parametrize("value", ["a\rb", "a\r", "a\r\n\rb"])
def test_mll_rejects_bare_cr(value):
    with pytest.raises(InvalidStringError):
        String.from_raw(value, StringType.MLL)


@pytest.mark.parametrize("value", ["a\r\nb", "a\nb"])
def test_mll_allows_line_endings(value):
    s = String.from_raw(value, StringType.MLL)
    assert s.as_string() == f"'''{value}'''"


def test_mlb_roundtrip_bare_cr():
    doc = parse("a = 1\n")
    doc["a"] = item("x\ry\r\nz", _parent=None) if False else String.from_raw("x\ry\r\nz", StringType.MLB)
    out = dumps(doc)
    assert parse(out)["a"] == "x\ry\r\nz"
