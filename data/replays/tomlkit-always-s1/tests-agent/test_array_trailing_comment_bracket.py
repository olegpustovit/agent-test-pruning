import tomlkit

from tomlkit import array


def test_trailing_comment_bracket_on_own_line():
    a = array()
    a.add_line(1, 2, comment="hi")
    assert a.as_string() == "[\n    1, 2, # hi\n]"


def test_trailing_comment_roundtrip_parses():
    a = array()
    a.add_line(1, 2, comment="hi")
    doc = tomlkit.document()
    doc["a"] = a
    parsed = tomlkit.parse(doc.as_string())
    assert parsed["a"] == [1, 2]


def test_comment_only_line_parses():
    a = array()
    a.add_line(comment="only")
    assert a.as_string() == "[\n    # only\n]"
    doc = tomlkit.document()
    doc["a"] = a
    assert tomlkit.parse(doc.as_string())["a"] == []


def test_trailing_comment_uses_trivia_indent():
    a = array()
    a.add_line(1, comment="c")
    a.trivia.indent = "  "
    assert a.as_string() == "[\n    1, # c\n  ]"


def test_plain_single_line_array_unchanged():
    assert array("[1, 2, 3]").as_string() == "[1, 2, 3]"
    assert array().as_string() == "[]"


def test_multiline_array_unchanged():
    a = array()
    a.multiline(True)
    a.extend([1, 2])
    assert a.as_string() == "[\n    1,\n    2,\n]"


def test_add_line_without_comment_unchanged():
    a = array()
    a.add_line(1, 2)
    assert a.as_string() == "[\n    1, 2,]"
