import sys

import pytest

from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


@pytest.mark.skipif(
    not hasattr(sys, "get_int_max_str_digits"),
    reason="int digit limit unavailable",
)
def test_overlong_decimal_integer_rejected():
    digits = sys.get_int_max_str_digits() or 0
    if not digits:
        pytest.skip("int digit limit disabled")
    with pytest.raises(TOMLKitError):
        parse("a = " + "9" * (digits + 10))


def test_float_literals_still_parse():
    doc = parse("a = 1.5\nb = 1e3\nc = inf\nd = -inf\ne = nan\nf = 1_0.5")
    assert doc["a"] == 1.5
    assert doc["b"] == 1000.0
    assert doc["c"] == float("inf")
    assert doc["d"] == float("-inf")
    assert doc["e"] != doc["e"]
    assert doc["f"] == 10.5


def test_non_decimal_bad_integer_rejected():
    with pytest.raises(TOMLKitError):
        parse("a = 0xZZ")
