from tomlkit import aot, dumps, parse, table


def test_scalar_inserted_before_dotted_super_table_with_header_child():
    doc = parse("a.b = 1\n")
    doc["a"]["c"] = table()
    doc["a"]["c"]["x"] = 1
    doc["z"] = 2

    out = dumps(doc)
    assert out.index("z = 2") < out.index("a.b")
    assert parse(out) == {"z": 2, "a": {"b": 1, "c": {"x": 1}}}


def test_scalar_inserted_before_dotted_table_with_aot_child():
    doc = parse("a.b = 1\n")
    children = aot()
    t = table()
    t["x"] = 1
    children.append(t)
    doc["a"]["c"] = children
    doc["z"] = 2

    out = dumps(doc)
    assert parse(out) == {"z": 2, "a": {"b": 1, "c": [{"x": 1}]}}


def test_scalar_inserted_before_nested_dotted_with_header_child():
    doc = parse("a.b.c = 1\n")
    doc["a"]["b"]["d"] = table()
    doc["a"]["b"]["d"]["x"] = 1
    doc["z"] = 2

    assert parse(dumps(doc)) == {"z": 2, "a": {"b": {"c": 1, "d": {"x": 1}}}}


def test_purely_inline_dotted_keys_unchanged():
    doc = parse("a.b = 1\n")
    doc["a"]["c"] = 2
    doc["z"] = 3

    assert dumps(doc) == "a.b = 1\na.c = 2\nz = 3\n"
