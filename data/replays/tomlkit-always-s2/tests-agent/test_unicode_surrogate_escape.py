import pytest

from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


@pytest.mark.parametrize(
    "esc", ["\\ud800", "\\uDFFF", "\\udabc", "\\U0000D800", "\\U0000dfff", "\\U0000DC00"]
)
def test_surrogate_escapes_rejected(esc):
    with pytest.raises(TOMLKitError):
        parse(f'a = "{esc}"')


@pytest.mark.parametrize(
    "esc,expected",
    [
        ("\\u0041", "A"),
        ("\\uD7FF", "퟿"),
        ("\\ue000", ""),
        ("\\U0000d7ff", "퟿"),
        ("\\U0000E000", ""),
        ("\\U0001F600", "\U0001f600"),
        ("\\U0010FFFF", "\U0010ffff"),
    ],
)
def test_valid_escapes(esc, expected):
    assert parse(f'a = "{esc}"')["a"] == expected


@pytest.mark.parametrize("esc", ["\\uZZZZ", "\\U00110000", "\\U0000+123"])
def test_invalid_escapes_rejected(esc):
    with pytest.raises(TOMLKitError):
        parse(f'a = "{esc}"')


def test_surrogate_in_multiline_string_rejected():
    with pytest.raises(TOMLKitError):
        parse('a = """x\\U0000D800"""')
