import pytest

import tomlkit


@pytest.mark.parametrize("text", ["a\nb", "a\rb", "a\r\nb"])
def test_item_comment_rejects_line_breaks(text):
    with pytest.raises(ValueError):
        tomlkit.item(1).comment(text)


@pytest.mark.parametrize("text", ["a\nb", "a\rb", "a\r\nb"])
def test_add_line_rejects_line_breaks(text):
    arr = tomlkit.array()
    with pytest.raises(ValueError):
        arr.add_line(1, comment=text)


def test_single_line_comment_still_works():
    assert tomlkit.item(1).comment("hi").trivia.comment == "# hi"
    arr = tomlkit.array()
    arr.add_line(1, comment="hi")
    assert "# hi" in arr.as_string()
