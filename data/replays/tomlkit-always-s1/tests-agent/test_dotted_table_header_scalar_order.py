from tomlkit import aot, parse, table, dumps


def test_scalar_inserted_before_dotted_key_with_table_child():
    doc = parse("a.b = 1\n")
    doc["a"]["c"] = {"x": 1}
    doc["z"] = 2
    out = dumps(doc)
    assert out.index("z = 2") < out.index("a.b")
    assert parse(out).unwrap() == {"z": 2, "a": {"b": 1, "c": {"x": 1}}}


def test_scalar_inserted_before_dotted_key_with_aot_child():
    doc = parse("a.b = 1\n")
    a = aot()
    a.append(table())
    a[0]["x"] = 1
    doc["a"]["c"] = a
    doc["z"] = 2
    assert parse(dumps(doc)).unwrap() == {"z": 2, "a": {"b": 1, "c": [{"x": 1}]}}


def test_scalar_inserted_before_nested_dotted_key_with_table_child():
    doc = parse("a.b.c = 1\n")
    doc["a"]["b"]["d"] = {"x": 1}
    doc["z"] = 2
    assert parse(dumps(doc)).unwrap() == {
        "z": 2,
        "a": {"b": {"c": 1, "d": {"x": 1}}},
    }


def test_purely_inline_dotted_keys_keep_scalar_after():
    doc = parse("a.b = 1\n")
    doc["a"]["c"] = 2
    doc["z"] = 3
    out = dumps(doc)
    assert out.index("a.b") < out.index("z = 3")
    assert parse(out).unwrap() == {"a": {"b": 1, "c": 2}, "z": 3}
