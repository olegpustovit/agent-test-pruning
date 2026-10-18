from tomlkit import dumps
from tomlkit import loads
from tomlkit import parse


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
    doc = parse(CONTENT)
    doc["bar"]["a"] = 1
    out = doc.as_string()
    assert loads(out) == {
        "foo": {"name": "foo", "a": {"name": "foo-a"}},
        "bar": {"a": 1},
        "baz": {"name": "baz"},
    }
    assert doc["bar"]["a"] == 1


def test_add_plain_value_to_out_of_order_table_with_leading_subtables():
    content = """\
[a.b]
x = 1

[c]
y = 2

[a]
z = 3
"""
    doc = parse(content)
    doc["a"]["new"] = "v"
    out = doc.as_string()
    assert loads(out) == {
        "a": {"b": {"x": 1}, "z": 3, "new": "v"},
        "c": {"y": 2},
    }
    assert dumps(loads(out)) == dumps(parse(out))
