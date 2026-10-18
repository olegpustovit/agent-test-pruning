import tomlkit


def test_add_line_trailing_comment_bracket_on_own_line():
    arr = tomlkit.array()
    arr.add_line(1, comment="hi")
    assert arr.as_string() == "[\n    1, # hi\n]"


def test_add_line_trailing_comment_roundtrips():
    arr = tomlkit.array()
    arr.add_line(1, 2, comment="hi")
    doc = tomlkit.document()
    doc["a"] = arr
    parsed = tomlkit.loads(tomlkit.dumps(doc))
    assert parsed["a"] == [1, 2]


def test_plain_single_line_array_unchanged():
    assert tomlkit.array("[1, 2]").as_string() == "[1, 2]"
    assert tomlkit.array().as_string() == "[]"
