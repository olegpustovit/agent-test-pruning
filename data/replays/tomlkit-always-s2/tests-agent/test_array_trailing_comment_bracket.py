import tomlkit

from tomlkit.items import Comment


def _trailing_comment_array():
    a = tomlkit.parse("a = [1, 2 # c\n]\n")["a"]
    # drop the final whitespace group so a Comment is the last rendered item
    a._value.pop()
    return a


def test_trailing_comment_bracket_on_own_line():
    a = _trailing_comment_array()
    assert isinstance(list(a._iter_items())[-1], Comment)
    out = a.as_string()
    assert out.endswith("# c\n]")
    doc = tomlkit.document()
    doc["a"] = a
    assert tomlkit.parse(doc.as_string())["a"] == [1, 2]


def test_plain_single_line_array_unchanged():
    assert tomlkit.parse("a = [1, 2]")["a"].as_string() == "[1, 2]"
    assert tomlkit.array().as_string() == "[]"


def test_add_line_with_comment_bracket_on_own_line():
    a = tomlkit.array()
    a.add_line(1, 2, comment="hi")
    assert a.as_string() == "[\n    1, 2, # hi\n]"
