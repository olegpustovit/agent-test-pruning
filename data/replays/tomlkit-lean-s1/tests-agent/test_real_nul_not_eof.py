import pytest

from tomlkit import parse
from tomlkit.exceptions import ParseError


@pytest.mark.parametrize(
    "doc",
    [
        "a = 1\x00",
        "\x00",
        "a = 1 # c\x00",
        "a = 1 # c\x00\n",
        "a = [1,\x00 2]",
        "a = {b = 1\x00}",
        "a\x00 = 1",
        "a = \x00",
        "[t\x00]",
    ],
)
def test_real_nul_is_rejected(doc):
    with pytest.raises(ParseError):
        parse(doc)


@pytest.mark.parametrize("doc", ["a = 1", "a = 1 # c", "a = [1,", 'a = "x', "[t", "a ="])
def test_truncated_input_errors_or_parses_without_hanging(doc):
    try:
        parse(doc)
    except ParseError:
        pass
