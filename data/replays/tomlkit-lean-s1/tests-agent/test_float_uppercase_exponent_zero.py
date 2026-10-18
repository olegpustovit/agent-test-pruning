import pytest

from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("0E2", 0.0),
        ("0E+2", 0.0),
        ("0E-2", 0.0),
        ("+0E2", 0.0),
        ("-0E2", -0.0),
        ("0e2", 0.0),
    ],
)
def test_zero_mantissa_exponent(raw, expected):
    doc = parse(f"a = {raw}")
    assert doc["a"] == expected
    assert isinstance(doc["a"], float)
    assert doc.as_string() == f"a = {raw}"


@pytest.mark.parametrize("raw", ["00E2", "01E2", "0_1E2"])
def test_leading_zero_still_rejected(raw):
    with pytest.raises(TOMLKitError):
        parse(f"a = {raw}")
