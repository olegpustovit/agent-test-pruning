import sys

import pytest

import tomlkit

from tomlkit.exceptions import TOMLKitError


needs_limit = pytest.mark.skipif(
    not hasattr(sys, "get_int_max_str_digits"),
    reason="int digit limit unavailable",
)


@needs_limit
def test_overlong_decimal_integer_rejected():
    limit = sys.get_int_max_str_digits()
    if limit == 0:
        pytest.skip("int digit limit disabled")
    with pytest.raises(TOMLKitError):
        tomlkit.parse("a = " + "1" * (limit + 1))


@needs_limit
def test_overlong_negative_integer_rejected():
    limit = sys.get_int_max_str_digits()
    if limit == 0:
        pytest.skip("int digit limit disabled")
    with pytest.raises(TOMLKitError):
        tomlkit.parse("a = -" + "9" * (limit + 1))


@pytest.mark.parametrize(
    "src,expected",
    [
        ("a = 1.5", 1.5),
        ("a = 1e3", 1000.0),
        ("a = -2.5e-1", -0.25),
        ("a = inf", float("inf")),
        ("a = -inf", float("-inf")),
        ("a = 42", 42),
        ("a = 0xff", 255),
        ("a = 1_000", 1000),
    ],
)
def test_valid_numbers_still_parse(src, expected):
    assert tomlkit.parse(src)["a"] == expected


def test_nan():
    v = tomlkit.parse("a = nan")["a"]
    assert v != v


@pytest.mark.parametrize("src", ["a = 0xzz", "a = 0b12", "a = 0o9", "a = 0x1.5"])
def test_bad_non_decimal_rejected(src):
    with pytest.raises(TOMLKitError):
        tomlkit.parse(src)
