from tomlkit import parse


def test_append_to_spaced_inline_table():
    doc = parse("a = {x = 1, y = 2}\n")
    doc["a"]["z"] = 3
    assert doc.as_string() == "a = {x = 1, y = 2, z = 3}\n"


def test_append_to_padded_inline_table_single_space():
    doc = parse("a = { foo = 1, bar = 2 }\n")
    doc["a"]["baz"] = 3
    out = doc.as_string()
    assert "  " not in out.replace("a = ", "a=")
    assert parse(out)["a"] == {"foo": 1, "bar": 2, "baz": 3}
