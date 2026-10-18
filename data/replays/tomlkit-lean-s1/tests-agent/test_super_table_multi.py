import tomlkit


def test_multiple_subtables_is_super_table():
    doc = tomlkit.parse("[a.b]\nx = 1\n[a.c]\ny = 2\n")
    assert doc["a"].is_super_table()
    assert tomlkit.dumps(doc) == "[a.b]\nx = 1\n[a.c]\ny = 2\n"


def test_mixed_children_not_super_table():
    doc = tomlkit.parse("[a]\nz = 1\n[a.b]\nx = 1\n[a.c]\ny = 2\n")
    assert not doc["a"].is_super_table()


def test_subtable_and_aot_is_super_table():
    doc = tomlkit.parse("[a.b]\nx = 1\n[[a.c]]\ny = 2\n")
    assert doc["a"].is_super_table()
