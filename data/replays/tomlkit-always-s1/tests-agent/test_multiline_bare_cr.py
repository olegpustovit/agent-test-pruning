import pytest

from tomlkit import dumps, loads
from tomlkit.exceptions import InvalidStringError
from tomlkit.items import String, StringType


def test_mlb_escapes_bare_cr():
    s = String.from_raw("a\rb", StringType.MLB)
    assert s.as_string() == '"""a\\rb"""'
    assert loads("x = " + s.as_string())["x"] == "a\rb"


def test_mlb_trailing_and_leading_bare_cr():
    assert String.from_raw("a\r", StringType.MLB).as_string() == '"""a\\r"""'
    assert String.from_raw("\rx", StringType.MLB).as_string() == '"""\\rx"""'


def test_mlb_keeps_crlf():
    s = String.from_raw("a\r\nb", StringType.MLB)
    assert s.as_string() == '"""a\r\nb"""'


@pytest.mark.parametrize("value", ["a\rb", "a\r", "\rx"])
def test_mll_rejects_bare_cr(value):
    with pytest.raises(InvalidStringError):
        String.from_raw(value, StringType.MLL)


def test_mll_accepts_crlf_and_lf():
    assert String.from_raw("a\r\nb", StringType.MLL).as_string() == "'''a\r\nb'''"
    assert String.from_raw("a\nb", StringType.MLL).as_string() == "'''a\nb'''"


def test_slb_sll_unchanged():
    with pytest.raises(InvalidStringError):
        String.from_raw("a\rb", StringType.SLL)
