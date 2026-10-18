import datetime

import pytest

import tomlkit
from tomlkit._utils import parse_rfc3339
from tomlkit.exceptions import ParseError


def test_escape_e():
    assert tomlkit.parse(r'a = "\e[0m"')["a"] == "\x1b[0m"


def test_escape_x():
    assert tomlkit.parse(r'a = "\x41\x7a"')["a"] == "Az"
    for bad in (r'a = "\x4"', r'a = "\xZZ"'):
        with pytest.raises(ParseError):
            tomlkit.parse(bad)


def test_optional_seconds():
    d = tomlkit.parse("a = 07:32\nb = 1979-05-27T07:32\nc = 1979-05-27 07:32Z\n")
    assert d["a"] == datetime.time(7, 32)
    assert d["b"] == datetime.datetime(1979, 5, 27, 7, 32)
    assert d["c"] == datetime.datetime(1979, 5, 27, 7, 32, tzinfo=datetime.timezone.utc)
    assert d.as_string().startswith("a = 07:32\n")


def test_parse_rfc3339():
    assert parse_rfc3339("07:32") == datetime.time(7, 32)
    assert parse_rfc3339("1979-05-27T07:32:01.5+02:00").utcoffset() == datetime.timedelta(
        hours=2
    )
    with pytest.raises(ValueError, match="RFC 3339"):
        parse_rfc3339("nope")


def test_inline_table_newlines_and_trailing_comma():
    src = "t = {\n  a = 1, # one\n  b = 2,\n}\n"
    d = tomlkit.parse(src)
    assert d["t"] == {"a": 1, "b": 2}
    assert d.as_string() == src


def test_inline_table_still_rejects_bad_commas():
    for bad in ("t = {a = 1 b = 2}", "t = {, a = 1}", "t = {a = 1,, b = 2}"):
        with pytest.raises(ParseError):
            tomlkit.parse(bad)


def test_bare_cr_rejected():
    with pytest.raises(ParseError):
        tomlkit.parse("a = 1 # c\rb = 2\n")
    with pytest.raises(ParseError):
        tomlkit.parse("a = 1\rb = 2\n")
    assert tomlkit.parse("a = 1\r\nb = 2\r\n")["b"] == 2


def test_nan_container_equality():
    d = tomlkit.parse("a = nan\nb = [nan]\n")
    assert d == {"a": float("nan"), "b": [float("nan")]}
    assert d != {"a": 1.0, "b": [float("nan")]}
