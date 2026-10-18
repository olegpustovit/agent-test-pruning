import tomlkit


def test_bool_items_compare_by_value():
    t1, t2, f1 = tomlkit.boolean("true"), tomlkit.boolean("true"), tomlkit.boolean("false")
    assert t1 == t2
    assert not (t1 != t2)
    assert t1 != f1
    assert f1 == tomlkit.boolean("false")
    assert t1 == True  # noqa: E712
    assert f1 != 1
