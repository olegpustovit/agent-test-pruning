import tomlkit


def _roundtrip(doc):
    out = tomlkit.dumps(doc)
    assert tomlkit.parse(out) == doc
    return out


def test_add_to_dotted_key_in_inline_table():
    doc = tomlkit.parse("a = {b.c = 1, d = 2}\n")
    doc["a"]["b"]["e"] = 3
    out = _roundtrip(doc)
    assert out == "a = {b.c = 1, b.e = 3, d = 2}\n"
    assert doc["a"]["b"]["e"] == 3


def test_add_to_nested_dotted_key_in_inline_table():
    doc = tomlkit.parse("a = {b.c.x = 1}\n")
    doc["a"]["b"]["c"]["y"] = 3
    doc["a"]["b"]["z"] = 4
    out = _roundtrip(doc)
    assert out == "a = {b.c.x = 1, b.c.y = 3, b.z = 4}\n"


def test_unmodified_dotted_inline_table_unchanged():
    text = "a = {b.c = 1, d = 2}\n"
    assert tomlkit.dumps(tomlkit.parse(text)) == text
