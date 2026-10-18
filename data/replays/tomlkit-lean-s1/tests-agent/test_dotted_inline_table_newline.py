import tomlkit


def test_newline_kept_after_dotted_inline_table_without_trailing_newline():
    doc = tomlkit.parse("a.b = {x = 1}")
    doc["c"] = 1
    assert doc.as_string() == "a.b = {x = 1}\nc = 1\n"
    assert tomlkit.parse(doc.as_string()) == {"a": {"b": {"x": 1}}, "c": 1}
