import tomlkit

CONTENT = """\
[foo]
name = "foo"

[bar.a.b]
name = "bar-a-b"

[foo.a]
name = "foo-a"

[bar.a]
name = "bar-a"

[baz]
name = "baz"

[bar.a.c]
name = "bar-a-c"
"""


def test_overwrite_out_of_order_table_with_plain_value():
    doc = tomlkit.parse(CONTENT)
    doc["bar"]["a"] = "plain"
    assert doc["bar"]["a"] == "plain"
    out = doc.as_string()
    reparsed = tomlkit.parse(out).unwrap()
    assert reparsed == doc.unwrap()
    assert reparsed["bar"]["a"] == "plain"
    assert reparsed["foo"] == {"name": "foo", "a": {"name": "foo-a"}}
    assert reparsed["baz"] == {"name": "baz"}


def test_overwrite_out_of_order_table_with_table_still_valid():
    doc = tomlkit.parse(CONTENT)
    doc["bar"]["a"] = {"name": "new"}
    reparsed = tomlkit.parse(doc.as_string()).unwrap()
    assert reparsed["bar"]["a"] == {"name": "new"}
    assert reparsed["foo"]["a"] == {"name": "foo-a"}


def test_overwrite_plain_value_in_out_of_order_table():
    doc = tomlkit.parse(
        '[a]\nx = 1\n\n[b]\ny = 1\n\n[a.c]\nz = 1\n'
    )
    doc["a"]["x"] = 2
    reparsed = tomlkit.parse(doc.as_string()).unwrap()
    assert reparsed["a"] == {"x": 2, "c": {"z": 1}}


def test_add_new_plain_value_to_out_of_order_table():
    doc = tomlkit.parse("[a.b]\nq = 1\n\n[c]\nd = 1\n\n[a]\nx = 1\n\n[a.e]\nz = 1\n")
    doc["a"]["new"] = "v"
    out = doc.as_string()
    reparsed = tomlkit.parse(out).unwrap()
    assert reparsed["a"]["new"] == "v"
    assert reparsed["a"]["x"] == 1
    assert reparsed["a"]["b"] == {"q": 1}
    assert reparsed["a"]["e"] == {"z": 1}
