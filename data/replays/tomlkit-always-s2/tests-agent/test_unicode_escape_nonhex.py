import pytest

from tomlkit import loads
from tomlkit.exceptions import TOMLKitError


@pytest.mark.parametrize(
    "esc",
    ["\\u+123", "\\u-123", "\\u1_23", "\\u 123", "\\u123 ", "\\u12g4", "\\u0x12"],
)
def test_short_escape_rejects_non_hex(esc):
    with pytest.raises(TOMLKitError):
        loads(f'a = "{esc}"')


@pytest.mark.parametrize(
    "esc",
    ["\\U+0000123", "\\U-0000123", "\\U0000_123", "\\U 0000123", "\\U0000012g"],
)
def test_long_escape_rejects_non_hex(esc):
    with pytest.raises(TOMLKitError):
        loads(f'a = "{esc}"')


def test_valid_escapes_still_work():
    doc = loads('a = "\\u00E9\\u00e9\\U0001F600\\U000000aB"')
    assert doc["a"] == "éé\U0001f600«"
