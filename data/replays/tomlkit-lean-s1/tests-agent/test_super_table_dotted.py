import tomlkit


def test_dotted_only_child_is_not_super_table():
    doc = tomlkit.parse("[a]\nb.c = 1\n")
    assert not doc["a"].is_super_table()
    assert tomlkit.dumps(doc) == "[a]\nb.c = 1\n"


def test_real_subtable_only_child_is_super_table():
    doc = tomlkit.parse("[a.b]\nc = 1\n")
    assert doc["a"].is_super_table()
    assert tomlkit.dumps(doc) == "[a.b]\nc = 1\n"


def test_non_table_only_child_is_not_super_table():
    doc = tomlkit.parse("[a]\nb = 1\n")
    assert not doc["a"].is_super_table()
