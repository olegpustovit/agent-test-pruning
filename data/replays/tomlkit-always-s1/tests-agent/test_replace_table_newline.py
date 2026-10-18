import tomlkit


DOC = """\
[a]
x = 1

[b]
y = 2
"""


def test_replace_last_table_with_trailing_newline_keeps_newline():
    doc = tomlkit.parse("[a]\nx = 1\n\n")
    doc["a"] = {"x": 2}
    assert doc.as_string() == "[a]\nx = 2\n\n"


def test_replace_middle_table_keeps_blank_line():
    doc = tomlkit.parse(DOC)
    doc["a"] = {"x": 5}
    assert doc.as_string() == "[a]\nx = 5\n\n[b]\ny = 2\n"


def test_replace_last_table_without_trailing_newline_adds_none():
    doc = tomlkit.parse("[a]\nx = 1\n")
    doc["a"] = {"x": 2}
    assert doc.as_string() == "[a]\nx = 2\n"

