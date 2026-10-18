import tomlkit


def test_add_dotted_key_to_super_table_renders_header():
    doc = tomlkit.parse("[a.b]\nx = 1\n")
    doc["a"].add(tomlkit.key(["c", "d"]), 1)
    out = doc.as_string()
    assert "[a]" in out
    assert tomlkit.parse(out) == {"a": {"b": {"x": 1}, "c": {"d": 1}}}


def test_add_dotted_key_to_super_table_exact_output():
    doc = tomlkit.parse("[a.b]\nx = 1\n")
    doc["a"].add(tomlkit.key(["c", "d"]), 1)
    assert doc.as_string() == "[a]\nc.d = 1\n\n[a.b]\nx = 1\n"


def test_plain_super_table_header_still_omitted():
    doc = tomlkit.parse("[a.b]\nx = 1\n")
    assert doc.as_string() == "[a.b]\nx = 1\n"
