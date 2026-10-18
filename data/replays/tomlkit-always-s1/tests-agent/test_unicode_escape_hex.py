import pytest

from tomlkit import parse
from tomlkit.exceptions import InvalidUnicodeValueError


@pytest.mark.parametrize(
    "esc",
    [
        r"\u+123", r"\u-123", r"\u 123", r"\u1_23", r"\u0x12", r"\u12 3",
        r"\U+0000041", r"\U0x000041", r"\U0000_041", r"\U-0000041", r"\U 0000041",
    ],
)
def test_non_hex_digits_rejected(esc):
    with pytest.raises(InvalidUnicodeValueError):
        parse(f's = "{esc}"')


@pytest.mark.parametrize(
    "esc, expected",
    [
        (r"A", "A"),
        (r"é", "é"),
        (r"é", "é"),
        (r"\U00000041", "A"),
        (r"\U0001F600", "\U0001f600"),
    ],
)
def test_valid_hex_escapes(esc, expected):
    assert parse(f's = "{esc}"')["s"] == expected
