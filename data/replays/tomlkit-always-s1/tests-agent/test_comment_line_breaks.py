import pytest

from tomlkit import array
from tomlkit import integer


@pytest.mark.parametrize("bad", ["a\nb", "a\rb", "a\r\nb", "\n"])
def test_item_comment_rejects_line_breaks(bad):
    with pytest.raises(ValueError, match="line breaks"):
        integer(1).comment(bad)


@pytest.mark.parametrize("bad", ["a\nb", "a\rb", "a\r\nb"])
def test_add_line_rejects_line_breaks(bad):
    a = array()
    with pytest.raises(ValueError, match="line breaks"):
        a.add_line(1, 2, comment=bad)
    assert len(a) == 0


def test_item_comment_valid():
    i = integer(1).comment("hello")
    assert i.trivia.comment == "# hello"


def test_add_line_valid_and_no_comment():
    a = array()
    a.add_line(1, 2, comment="ok")
    a.add_line(3)
    assert list(a) == [1, 2, 3]
    assert "# ok" in a.as_string()
