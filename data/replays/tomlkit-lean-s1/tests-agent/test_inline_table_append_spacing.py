import tomlkit


def test_append_to_compact_spaced_table_uses_comma_space():
    doc = tomlkit.parse("a = {x = 1, y = 2}\n")
    doc["a"]["z"] = 3
    assert doc.as_string() == "a = {x = 1, y = 2, z = 3}\n"


def test_append_to_padded_table_no_double_space():
    doc = tomlkit.parse("a = { foo = 1, bar = 2 }\n")
    doc["a"]["baz"] = 3
    out = doc.as_string()
    assert "  " not in out
    assert tomlkit.parse(out)["a"] == {"foo": 1, "bar": 2, "baz": 3}
