import tomlkit


def test_replace_final_table_with_trailing_blank_line():
    doc = tomlkit.parse("[a]\nx = 1\n\n[b]\ny = 2\n\n")
    new = tomlkit.table()
    new.add("z", 3)
    doc["b"] = new
    assert doc.as_string() == "[a]\nx = 1\n\n[b]\nz = 3\n\n"
