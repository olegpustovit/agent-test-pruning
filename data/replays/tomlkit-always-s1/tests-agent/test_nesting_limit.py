import pytest

from tomlkit import loads
from tomlkit import parse
from tomlkit.exceptions import ParseError
from tomlkit.parser import Parser

LIMIT = Parser.MAX_NESTING_DEPTH


def test_limit_is_100():
    assert LIMIT == 100


@pytest.mark.parametrize(
    "open_, close",
    [("[", "]"), ("{a=", "}")],
)
def test_value_nesting_at_limit_parses(open_, close):
    doc = parse("x = " + open_ * LIMIT + "1" + close * LIMIT)
    assert doc.as_string() == "x = " + open_ * LIMIT + "1" + close * LIMIT


@pytest.mark.parametrize(
    "open_, close",
    [("[", "]"), ("{a=", "}")],
)
def test_value_nesting_beyond_limit_raises(open_, close):
    n = LIMIT + 1
    with pytest.raises(ParseError, match="nested more than"):
        parse("x = " + open_ * n + "1" + close * n)


def test_mixed_nesting_beyond_limit_raises():
    n = LIMIT // 2 + 1
    with pytest.raises(ParseError):
        parse("x = " + "[{a=" * n + "1" + "}]" * n)


def test_huge_nesting_does_not_recursion_error():
    with pytest.raises(ParseError):
        parse("x = " + "[" * 100000)


def test_depth_resets_between_siblings():
    src = "x = " + "[" * 60 + "1" + "]" * 60 + "\ny = " + "[" * 60 + "1" + "]" * 60
    assert parse(src).as_string() == src


def test_depth_resets_after_many_sequential_values():
    src = "x = [" + ",".join(["[1]"] * 500) + "]"
    assert parse(src).as_string() == src


def test_dotted_key_at_limit_parses():
    key = ".".join(["a"] * LIMIT)
    doc = parse(f"{key} = 1")
    assert doc.as_string() == f"{key} = 1"


def test_dotted_key_beyond_limit_raises():
    key = ".".join(["a"] * (LIMIT + 1))
    with pytest.raises(ParseError, match="more than"):
        parse(f"{key} = 1")


def test_huge_dotted_key_does_not_recursion_error():
    with pytest.raises(ParseError):
        parse(".".join(["a"] * 50000) + " = 1")


def test_dotted_table_header_beyond_limit_raises():
    key = ".".join(["a"] * (LIMIT + 1))
    with pytest.raises(ParseError):
        parse(f"[{key}]\nx = 1")


def test_dotted_key_fragments_and_formatting_preserved():
    src = 'a . "b c" .d\t= 1\n'
    doc = loads(src)
    assert doc.as_string() == src
    assert doc["a"]["b c"]["d"] == 1


def test_quoted_dotted_key_beyond_limit_raises():
    key = ".".join(['"a"'] * (LIMIT + 1))
    with pytest.raises(ParseError):
        parse(f"{key} = 1")
