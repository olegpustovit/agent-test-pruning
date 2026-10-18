import pytest

import tomlkit


@pytest.mark.parametrize("bad", ["a\nb", "a\rb", "a\r\nb", "\n"])
def test_item_comment_rejects_line_breaks(bad):
    item = tomlkit.item(1)
    with pytest.raises(ValueError, match="line breaks"):
        item.comment(bad)


@pytest.mark.parametrize("bad", ["a\nb", "a\rb", "a\r\nb"])
def test_add_line_rejects_line_breaks(bad):
    arr = tomlkit.array()
    with pytest.raises(ValueError, match="line breaks"):
        arr.add_line(1, 2, comment=bad)
    assert len(arr) == 0


def test_valid_comments_still_work():
    item = tomlkit.item(1).comment("hello")
    assert item.trivia.comment == "# hello"
    arr = tomlkit.array()
    arr.add_line(1, 2, comment="note")
    arr.add_line(3, comment=None)
    assert "# note" in arr.as_string()
    assert arr == [1, 2, 3]
