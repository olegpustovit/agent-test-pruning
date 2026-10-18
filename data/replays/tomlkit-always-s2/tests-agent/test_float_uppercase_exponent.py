import pytest

from tomlkit import loads, parse
from tomlkit.exceptions import ParseError


@pytest.mark.parametrize(
    "text, expected",
    [
        ("0E2", 0.0),
        ("0E+2", 0.0),
        ("0E-2", 0.0),
        ("+0E2", 0.0),
        ("-0E2", -0.0),
        ("0e2", 0.0),
        ("0E0", 0.0),
        ("1E2", 100.0),
    ],
)
def test_zero_mantissa_exponent(text, expected):
    doc = parse(f"a = {text}")
    assert doc["a"] == expected
    assert isinstance(doc["a"], float)
    assert doc.as_string() == f"a = {text}"


def test_uppercase_exponent_in_array():
    assert loads("a = [0E2, 0e2]")["a"] == [0.0, 0.0]


@pytest.mark.parametrize("text", ["00E2", "01E2", "0E", "00", "01"])
def test_invalid_leading_zero_still_rejected(text):
    with pytest.raises(ParseError):
        parse(f"a = {text}")
