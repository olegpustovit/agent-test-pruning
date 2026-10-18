import tomlkit


def test_table_replaced_by_value_moves_before_tables():
    d = tomlkit.parse("[a]\nx=1\n\n[b]\ny=2\n\n[c]\nz=3\n")
    d["b"] = 5
    out = tomlkit.dumps(d)
    assert out == "b = 5\n\n[a]\nx=1\n\n[c]\nz=3\n"
    r = tomlkit.parse(out)
    assert r["b"] == 5
    assert "b" not in r["a"]
    assert r["a"] == {"x": 1}
    assert r["c"] == {"z": 3}


def test_last_table_replaced_by_value_roundtrip():
    d = tomlkit.parse("top = 1\n[a]\nx=1\n[b]\ny=2\n")
    d["b"] = "s"
    r = tomlkit.parse(tomlkit.dumps(d))
    assert r["b"] == "s"
    assert r["top"] == 1
    assert r["a"] == {"x": 1}


def test_value_replaced_by_table_still_works():
    d = tomlkit.parse("a = 1\nb = 2\n[t]\nz=3\n")
    d["a"] = {"k": 1}
    r = tomlkit.parse(tomlkit.dumps(d))
    assert r["a"] == {"k": 1}
    assert r["b"] == 2
    assert r["t"] == {"z": 3}
