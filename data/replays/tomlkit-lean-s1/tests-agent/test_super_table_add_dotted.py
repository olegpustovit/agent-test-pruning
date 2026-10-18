import tomlkit


def test_add_dotted_key_to_super_table_renders_header():
    doc = tomlkit.parse("[a.b]\nc = 1\n")
    doc["a"].add(tomlkit.key(["x", "y"]), 1)

    out = tomlkit.dumps(doc)
    assert out == "[a]\nx.y = 1\n\n[a.b]\nc = 1\n"

    reparsed = tomlkit.parse(out)
    assert reparsed == {"a": {"x": {"y": 1}, "b": {"c": 1}}}


def test_super_table_without_dotted_keys_has_no_header():
    doc = tomlkit.parse("[a.b]\nc = 1\n")
    assert tomlkit.dumps(doc) == "[a.b]\nc = 1\n"
