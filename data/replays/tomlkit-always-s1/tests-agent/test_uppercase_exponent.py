import pytest

from tomlkit import loads
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
        ("0.0E2", 0.0),
    ],
)
def test_zero_mantissa_exponent(raw, expected):
    doc = loads(f"a = {raw}")
    assert doc["a"] == expected
    assert isinstance(doc["a"], float)
    assert doc.as_string() == f"a = {raw}"


@pytest.mark.parametrize("raw", ["00E2", "01E2", "00e2"])
def test_leading_zeros_still_rejected(raw):
    with pytest.raises(TOMLKitError):
        loads(f"a = {raw}")
