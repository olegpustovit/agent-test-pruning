import datetime

import pytest

from tomlkit import dumps
from tomlkit import loads
from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


def test_escape_e_and_x():
    doc = parse(r's = "a\e\x41\x7f"')
    assert doc["s"] == "a\x1bA\x7f"
    assert doc.as_string() == r's = "a\e\x41\x7f"'


def test_invalid_hex_escape():
    with pytest.raises(TOMLKitError):
        parse(r's = "\x4"')
    with pytest.raises(TOMLKitError):
        parse(r's = "\xZZ"')


def test_datetime_without_seconds():
    doc = parse("a = 1979-05-27T07:32\nb = 07:32\nc = 1979-05-27 07:32Z\nd = 1979-05-27T07:32-07:00")
    assert doc["a"] == datetime.datetime(1979, 5, 27, 7, 32)
    assert doc["b"] == datetime.time(7, 32)
    assert doc["c"].utcoffset() == datetime.timedelta(0)
    assert doc["d"].utcoffset() == datetime.timedelta(hours=-7)
    assert doc.as_string().startswith("a = 1979-05-27T07:32\nb = 07:32\n")


def test_inline_table_newlines_trailing_comma_comments():
    src = 'a = {\n  x = 1, # one\n  y = 2,\n  # c\n}\n'
    doc = parse(src)
    assert doc["a"] == {"x": 1, "y": 2}
    assert doc.as_string() == src
    assert loads("a = {x = 1,}")["a"] == {"x": 1}
    assert loads("a = {\n}")["a"] == {}


@pytest.mark.parametrize("src", ["a = {,}", "a = {x = 1,,}", "a = {x = 1 y = 2}", "a = {,x = 1}"])
def test_inline_table_invalid(src):
    with pytest.raises(TOMLKitError):
        parse(src)


@pytest.mark.parametrize("src", ['a = 1\rb = 2', 'a = "x\ry"', 'a = """x\ry"""', "# c\rd = 1"])
def test_bare_cr_rejected(src):
    with pytest.raises(TOMLKitError):
        parse(src)


def test_crlf_ok():
    assert parse("a = 1\r\nb = 2\r\n")["b"] == 2


def test_nan_container_equality():
    assert loads("a = nan\nb = [nan]") == {"a": float("nan"), "b": [float("nan")]}
    assert loads("a = nan") != {"a": 1.0}
    assert loads("a = 1") != {"b": 1}
