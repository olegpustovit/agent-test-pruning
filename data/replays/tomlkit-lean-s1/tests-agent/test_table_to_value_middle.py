import tomlkit


def test_replace_middle_table_with_value_roundtrips():
    doc = tomlkit.parse("[a]\nx = 1\n\n[b]\ny = 2\n\n[c]\nz = 3\n")
    doc["b"] = 42
    out = doc.as_string()
    reparsed = tomlkit.parse(out)
    assert reparsed["b"] == 42
    assert reparsed["a"] == {"x": 1}
    assert reparsed["c"] == {"z": 3}
    assert out.index("b = 42") < out.index("[a]")


def test_replace_first_table_with_value_roundtrips():
    doc = tomlkit.parse("[a]\nx = 1\n\n[b]\ny = 2\n")
    doc["a"] = "s"
    reparsed = tomlkit.parse(doc.as_string())
    assert reparsed.unwrap() == {"a": "s", "b": {"y": 2}}
