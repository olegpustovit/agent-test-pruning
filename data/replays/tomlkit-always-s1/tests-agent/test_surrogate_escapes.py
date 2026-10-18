import pytest

from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


@pytest.mark.parametrize(
    "esc",
    [
        r"\ud800",
        r"\uDFFF",
        r"\udc00",
        r"\U0000d800",
        r"\U0000DFFF",
        r"\U0000dabc",
        r"\u00zz",
        r"\U0000zzzz",
    ],
)
def test_invalid_escapes_rejected(esc):
    with pytest.raises(TOMLKitError):
        parse(f'a = "{esc}"')


@pytest.mark.parametrize(
    "esc, expected",
    [
        (r"퟿", "퟿"),
        (r"", ""),
        (r"\U0000D7FF", "퟿"),
        (r"\U0000E000", ""),
        (r"\U0001F600", "\U0001f600"),
        (r"A", "A"),
        (r"\U00000041", "A"),
    ],
)
def test_valid_escapes_accepted(esc, expected):
    assert parse(f'a = "{esc}"')["a"] == expected
