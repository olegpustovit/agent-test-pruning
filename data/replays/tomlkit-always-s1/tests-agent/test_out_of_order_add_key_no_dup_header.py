import tomlkit

DOC = """\
[x.a]
v = 1

[x.b]
w = 2

[x]
p = 1
"""

DOC_EMPTY_X = """\
[x.a]
v = 1

[x]

[x.b]
w = 2
"""


def test_add_key_no_duplicate_header():
    doc = tomlkit.parse("[x.a]\nv = 1\n\n[x]\n")
    doc["x"]["k"] = 5
    out = doc.as_string()
    assert out.count("[x]") == 1
    assert tomlkit.parse(out) == {"x": {"a": {"v": 1}, "k": 5}}


def test_add_key_out_of_order_with_two_subtables():
    doc = tomlkit.parse("[x.a]\nv = 1\n\n[x.b]\nw = 2\n\n[x]\n")
    doc["x"]["k"] = "s"
    out = doc.as_string()
    assert out.count("[x]") == 1
    assert tomlkit.parse(out) == {"x": {"a": {"v": 1}, "b": {"w": 2}, "k": "s"}}


def test_add_key_sits_under_existing_header():
    doc = tomlkit.parse("[x.a]\nv = 1\n\n[x]\n")
    doc["x"]["k"] = 5
    out = doc.as_string()
    assert out.index("[x]\n") < out.index("k = 5")


def test_existing_plain_value_part_still_preferred():
    doc = tomlkit.parse(DOC)
    doc["x"]["k"] = 3
    out = doc.as_string()
    assert out.count("[x]") == 1
    assert tomlkit.parse(out) == {
        "x": {"a": {"v": 1}, "b": {"w": 2}, "p": 1, "k": 3}
    }


def test_roundtrip_unmodified_and_add_to_empty_concrete_middle():
    doc = tomlkit.parse(DOC_EMPTY_X)
    assert doc.as_string() == DOC_EMPTY_X
    doc["x"]["k"] = 1
    out = doc.as_string()
    assert out.count("[x]") == 1
    assert tomlkit.parse(out) == {"x": {"a": {"v": 1}, "b": {"w": 2}, "k": 1}}
