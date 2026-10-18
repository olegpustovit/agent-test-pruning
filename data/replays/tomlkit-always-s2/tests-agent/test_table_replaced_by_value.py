import tomlkit


DOC = "a = 1\n[t1]\nx = 1\n[t2]\ny = 2\n[t3]\nz = 3\n"


def test_table_replaced_by_value_roundtrips_as_root_key():
    d = tomlkit.parse(DOC)
    d["t2"] = 5
    out = tomlkit.dumps(d)
    back = tomlkit.parse(out)
    assert back["t2"] == 5
    assert back["t1"] == {"x": 1}
    assert "t2" not in back["t1"]
    assert back["t3"] == {"z": 3}
    assert out.index("t2 = 5") < out.index("[t1]")


def test_last_table_replaced_by_value():
    d = tomlkit.parse(DOC)
    d["t3"] = "v"
    back = tomlkit.parse(tomlkit.dumps(d))
    assert back == {"a": 1, "t1": {"x": 1}, "t2": {"y": 2}, "t3": "v"}
    assert tomlkit.dumps(d).index('t3 = "v"') < tomlkit.dumps(d).index("[t1]")


def test_value_replaced_by_table_still_works():
    d = tomlkit.parse("a = 1\nb = 2\n[t1]\nx = 1\n")
    d["a"] = {"k": 1}
    back = tomlkit.parse(tomlkit.dumps(d))
    assert back == {"b": 2, "a": {"k": 1}, "t1": {"x": 1}}
