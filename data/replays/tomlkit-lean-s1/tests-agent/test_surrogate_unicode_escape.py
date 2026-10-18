import pytest

from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


@pytest.mark.parametrize(
    "esc", ["\\ud800", "\\uDFFF", "\\U0000D800", "\\U0000dfff", "\\U0000DABC"]
)
def test_surrogate_escape_rejected(esc):
    with pytest.raises(TOMLKitError):
        parse(f'a = "{esc}"')


@pytest.mark.parametrize(
    "esc,expected",
    [
        ("\\ud7ff", "퟿"),
        ("\\ue000", ""),
        ("\\U0000D7FF", "퟿"),
        ("\\U0000E000", ""),
        ("\\U00010000", "\U00010000"),
    ],
)
def test_non_surrogate_escape_accepted(esc, expected):
    assert parse(f'a = "{esc}"')["a"] == expected


def test_non_hex_escape_rejected():
    with pytest.raises(TOMLKitError):
        parse('a = "\\u12g4"')


@pytest.mark.parametrize(
    "esc",
    ["\\u+123", "\\u-123", "\\u1_23", "\\u 123", "\\u123 ", "\\U+0000123", "\\U0000_123"],
)
def test_int_only_hex_forms_rejected(esc):
    with pytest.raises(TOMLKitError):
        parse(f'a = "{esc}"')
