import pytest

import tomlkit

from tomlkit.exceptions import UnexpectedCharError
from tomlkit.exceptions import UnexpectedEofError


@pytest.mark.parametrize("doc", ["[[a]\n", "[[a] x\n", "[[a] # c\n", "[[a]\n[x]\n"])
def test_aot_missing_second_bracket_unexpected_char(doc):
    with pytest.raises(UnexpectedCharError):
        tomlkit.parse(doc)


def test_aot_missing_second_bracket_eof():
    with pytest.raises(UnexpectedEofError):
        tomlkit.parse("[[a]")


def test_valid_aot_header_still_parses():
    text = "[[a]]\nx = 1\n[[a]] # c\nx = 2\n"
    doc = tomlkit.parse(text)
    assert doc["a"][1]["x"] == 2
    assert doc.as_string() == text
