import datetime
import math

import pytest

import tomlkit

from tomlkit.exceptions import TOMLKitError
from tomlkit._utils import parse_rfc3339


def test_escape_e():
    assert tomlkit.parse('a = "\\e[0m"')["a"] == "\x1b[0m"


def test_escape_x():
    assert tomlkit.parse('a = "\\x41\\x7a"')["a"] == "Az"


@pytest.mark.parametrize("bad", ['a = "\\x4"', 'a = "\\xZZ"'])
def test_bad_escape_x(bad):
    with pytest.raises(TOMLKitError):
        tomlkit.parse(bad)


def test_datetime_without_seconds():
    d = tomlkit.parse("a = 1979-05-27T07:32")["a"]
    assert d == datetime.datetime(1979, 5, 27, 7, 32)
    d = tomlkit.parse("a = 1979-05-27 07:32Z")["a"]
    assert d == datetime.datetime(1979, 5, 27, 7, 32, tzinfo=datetime.timezone.utc)
    d = tomlkit.parse("a = 1979-05-27T07:32-07:00")["a"]
    assert d.utcoffset() == datetime.timedelta(hours=-7)


def test_time_without_seconds():
    assert tomlkit.parse("a = 07:32")["a"] == datetime.time(7, 32)


def test_roundtrip_short_times():
    text = "a = 1979-05-27T07:32\nb = 07:32\n"
    assert tomlkit.parse(text).as_string() == text


def test_parse_rfc3339_errors():
    with pytest.raises(ValueError, match="RFC 3339"):
        parse_rfc3339("nope")
    assert parse_rfc3339("07:32:10.5") == datetime.time(7, 32, 10, 500000)


def test_inline_table_newlines_and_trailing_comma():
    text = "a = {\n  x = 1,\n  y = 2,\n}\n"
    doc = tomlkit.parse(text)
    assert doc["a"] == {"x": 1, "y": 2}
    assert doc.as_string() == text


def test_inline_table_comments():
    text = "a = {\n  # hi\n  x = 1, # c\n  y = 2\n}\n"
    doc = tomlkit.parse(text)
    assert doc.unwrap() == {"a": {"x": 1, "y": 2}}
    assert doc.as_string() == text


@pytest.mark.parametrize(
    "text",
    ["a = {,}", "a = {,x=1}", "a = {x=1,,y=2}", "a = {x=1 y=2}", "a = {x=1,"],
)
def test_inline_table_invalid(text):
    with pytest.raises(TOMLKitError):
        tomlkit.parse(text)


def test_inline_table_modify():
    doc = tomlkit.parse("a = {x = 1, y = 2}")
    doc["a"]["z"] = 3
    assert tomlkit.parse(doc.as_string())["a"] == {"x": 1, "y": 2, "z": 3}


def test_new_inline_table_output():
    t = tomlkit.inline_table()
    t["x"] = 1
    t["y"] = 2
    assert t.as_string() == "{x = 1, y = 2}"


def test_bare_cr_rejected():
    for text in ["a = 1\rb = 2\n", "# c\rd\n", 'a = """x\ry"""']:
        with pytest.raises(TOMLKitError):
            tomlkit.parse(text)


def test_crlf_accepted():
    doc = tomlkit.parse("a = 1\r\n# c\r\nb = 'x'\r\n")
    assert doc.unwrap() == {"a": 1, "b": "x"}


def test_nan_equality():
    doc = tomlkit.parse("a = nan\nb = [nan, 1.0]\n")
    assert doc == {"a": math.nan, "b": [math.nan, 1.0]}
    assert doc != {"a": math.nan, "b": [math.nan, 2.0]}
    assert doc != {"a": math.nan}
