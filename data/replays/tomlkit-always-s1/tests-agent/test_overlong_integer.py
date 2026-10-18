import sys

import pytest

from tomlkit import loads
from tomlkit.exceptions import ParseError


needs_limit = pytest.mark.skipif(
    not hasattr(sys, "get_int_max_str_digits"),
    reason="int digit limit unavailable",
)


@needs_limit
def test_overlong_decimal_integer_rejected():
    digits = "1" * (sys.get_int_max_str_digits() + 10)
    with pytest.raises(ParseError):
        loads(f"a = {digits}")


@needs_limit
def test_overlong_negative_decimal_integer_rejected():
    digits = "9" * (sys.get_int_max_str_digits() + 10)
    with pytest.raises(ParseError):
        loads(f"a = -{digits}")


@pytest.mark.parametrize(
    "src, expected",
    [("1.5", 1.5), ("1e3", 1000.0), ("-2.5e-1", -0.25), ("1_0.5", 10.5)],
)
def test_floats_still_parse(src, expected):
    assert loads(f"a = {src}")["a"] == expected


def test_inf_nan():
    doc = loads("a = inf\nb = -inf\nc = nan")
    assert doc["a"] == float("inf")
    assert doc["b"] == float("-inf")
    assert doc["c"] != doc["c"]


def test_integers_still_parse():
    doc = loads("a = 123\nb = 0xff\nc = 0o7\nd = 0b11")
    assert doc["a"] == 123 and doc["b"] == 255 and doc["c"] == 7 and doc["d"] == 3


def test_invalid_hex_not_float():
    with pytest.raises(ParseError):
        loads("a = 0xzz")
