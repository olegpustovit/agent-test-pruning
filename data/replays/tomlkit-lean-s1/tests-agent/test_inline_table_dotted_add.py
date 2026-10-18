import tomlkit


def _roundtrip(doc):
    out = tomlkit.dumps(doc)
    assert tomlkit.parse(out) == doc
    return out


def test_add_to_dotted_key_in_inline_table():
    doc = tomlkit.parse("t = {a.b = 1, a.c = 2}\n")
    doc["t"]["a"]["d"] = 3
    out = _roundtrip(doc)
    assert out == "t = {a.b = 1, a.d = 3, a.c = 2}\n"
    assert doc["t"]["a"] == {"b": 1, "d": 3, "c": 2}


def test_add_to_nested_dotted_key_in_inline_table():
    doc = tomlkit.parse("t = {a.b.c = 1}\n")
    doc["t"]["a"]["b"]["e"] = 3
    out = _roundtrip(doc)
    assert out == "t = {a.b.c = 1, a.b.e = 3}\n"
