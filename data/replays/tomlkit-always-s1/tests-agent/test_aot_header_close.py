import pytest

from tomlkit import loads
from tomlkit.exceptions import UnexpectedCharError
from tomlkit.exceptions import UnexpectedEofError


def test_valid_aot_header():
    doc = loads("[[a]]\nx = 1\n[[a]]\nx = 2\n")
    assert [t["x"] for t in doc["a"]] == [1, 2]


def test_valid_aot_header_with_comment_and_spaces():
    doc = loads("[[a]]  # c\nx = 1\n")
    assert doc["a"][0]["x"] == 1


def test_aot_missing_second_bracket_eof():
    with pytest.raises(UnexpectedEofError):
        loads("[[a]")


@pytest.mark.parametrize("src", ["[[a]\nx = 1\n", "[[a]x\n", "[[a] ]\n", "[[a]=1\n"])
def test_aot_missing_second_bracket_unexpected_char(src):
    with pytest.raises(UnexpectedCharError):
        loads(src)
