import pytest

from tomlkit import parse
from tomlkit.exceptions import UnexpectedCharError
from tomlkit.exceptions import UnexpectedEofError


@pytest.mark.parametrize("doc", ["[[a]\n", "[[a]x\n", "[[a] ]\n"])
def test_aot_header_missing_second_bracket_char(doc):
    with pytest.raises(UnexpectedCharError):
        parse(doc)


def test_aot_header_missing_second_bracket_eof():
    with pytest.raises(UnexpectedEofError):
        parse("[[a]")


def test_aot_header_valid():
    assert parse("[[a]]\nx = 1\n")["a"][0]["x"] == 1
