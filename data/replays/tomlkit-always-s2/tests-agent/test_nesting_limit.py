import pytest

import tomlkit

from tomlkit.exceptions import ParseError


LIMIT = 100


def test_array_at_limit_parses():
    doc = tomlkit.parse("a=" + "[" * LIMIT + "]" * LIMIT)
    assert doc.unwrap() == {"a": eval("[" * LIMIT + "]" * LIMIT)}


def test_array_beyond_limit_raises():
    with pytest.raises(ParseError):
        tomlkit.parse("a=" + "[" * (LIMIT + 1) + "]" * (LIMIT + 1))


def test_inline_table_at_limit_parses():
    tomlkit.parse("a=" + "{a=" * LIMIT + "1" + "}" * LIMIT)


def test_inline_table_beyond_limit_raises():
    with pytest.raises(ParseError):
        tomlkit.parse("a=" + "{a=" * (LIMIT + 1) + "1" + "}" * (LIMIT + 1))


def test_mixed_nesting_beyond_limit_raises():
    with pytest.raises(ParseError):
        tomlkit.parse("a=" + "[{a=" * 51 + "1" + "}]" * 51)


def test_dotted_key_at_limit_parses():
    key = ".".join(["a"] * LIMIT)
    doc = tomlkit.parse(f"{key} = 1")
    assert doc.as_string() == f"{key} = 1"


def test_dotted_key_beyond_limit_raises():
    key = ".".join(["a"] * (LIMIT + 1))
    with pytest.raises(ParseError):
        tomlkit.parse(f"{key} = 1")


def test_quoted_dotted_key_beyond_limit_raises():
    key = ".".join(['"a"'] * (LIMIT + 1))
    with pytest.raises(ParseError):
        tomlkit.parse(f"{key} = 1")


def test_very_deep_input_does_not_recursion_error():
    with pytest.raises(ParseError):
        tomlkit.parse("a=" + "[" * 100000)


def test_depth_counter_resets_between_siblings():
    # many sibling nested values must not accumulate depth
    src = "\n".join(f"k{i} = [[[1]]]" for i in range(300))
    assert len(tomlkit.parse(src)) == 300


def test_dotted_key_roundtrip_with_spaces():
    src = 'a . "b" . c = 1\n'
    assert tomlkit.parse(src).as_string() == src
    assert tomlkit.parse(src).unwrap() == {"a": {"b": {"c": 1}}}
