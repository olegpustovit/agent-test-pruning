from tomlkit import aot, parse, table


def test_scalar_before_dotted_key_with_table_child():
    doc = parse("a.b = 1\n")
    doc["a"]["c"] = table()
    doc["a"]["c"]["x"] = 1
    doc["z"] = 2
    out = doc.as_string()
    assert out.index("z = 2") < out.index("a.b")
    assert parse(out).unwrap() == {"a": {"b": 1, "c": {"x": 1}}, "z": 2}


def test_scalar_before_dotted_key_with_aot_child():
    doc = parse("a.b = 1\n")
    t = table()
    t["x"] = 1
    doc["a"]["c"] = aot()
    doc["a"]["c"].append(t)
    doc["z"] = 2
    assert parse(doc.as_string()).unwrap() == {
        "a": {"b": 1, "c": [{"x": 1}]},
        "z": 2,
    }


def test_inline_dotted_key_scalar_appended_after():
    doc = parse("a.b = 1\n")
    doc["a"]["d"] = 3
    doc["z"] = 2
    out = doc.as_string()
    assert out.index("a.b") < out.index("z = 2")
    assert parse(out).unwrap() == {"a": {"b": 1, "d": 3}, "z": 2}
