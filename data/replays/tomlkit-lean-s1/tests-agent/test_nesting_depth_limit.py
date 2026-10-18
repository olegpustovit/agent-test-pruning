import pytest

from tomlkit import parse
from tomlkit.exceptions import ParseError


def _nested_arrays(depth):
    return "a = " + "[" * depth + "]" * depth


def _nested_tables(depth):
    return "a = " + "{ a = " * (depth - 1) + "{}" + " }" * (depth - 1)


@pytest.mark.parametrize("build", [_nested_arrays, _nested_tables])
def test_value_nesting_at_limit_parses(build):
    assert parse(build(100))["a"] is not None


@pytest.mark.parametrize("build", [_nested_arrays, _nested_tables])
def test_value_nesting_beyond_limit_raises(build):
    with pytest.raises(ParseError):
        parse(build(101))


@pytest.mark.parametrize("build", [_nested_arrays, _nested_tables])
def test_very_deep_value_does_not_recurse_error(build):
    with pytest.raises(ParseError):
        parse(build(100000))


def test_depth_counter_resets_between_siblings():
    doc = parse("a = " + "[" * 60 + "]" * 60 + "\nb = " + "[" * 60 + "]" * 60)
    assert "a" in doc and "b" in doc


def _dotted(n):
    return ".".join("k%d" % i for i in range(n)) + " = 1"


def test_dotted_key_at_limit_parses():
    assert parse(_dotted(100))["k0"] is not None


def test_dotted_key_beyond_limit_raises():
    with pytest.raises(ParseError):
        parse(_dotted(101))


def test_very_long_dotted_key_raises():
    with pytest.raises(ParseError):
        parse(_dotted(50000))


def test_dotted_key_roundtrip_and_quoted_fragments():
    src = 'a . "b c" . d = 1\n'
    doc = parse(src)
    assert doc.as_string() == src
    assert doc["a"]["b c"]["d"] == 1
