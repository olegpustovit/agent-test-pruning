import tomlkit


DOC = """\
[x.a]
v = 1

[x.b]
w = 2

[x]
"""


def test_add_key_to_out_of_order_table_reuses_concrete_header():
    doc = tomlkit.parse(DOC)
    doc["x"]["k"] = 5
    out = doc.as_string()
    assert out.count("[x]") == 1
    assert tomlkit.parse(out) == {"x": {"a": {"v": 1}, "b": {"w": 2}, "k": 5}}
    assert out.index("[x]") > out.index("[x.b]")
    assert out.index("k = 5") > out.index("[x]\n")
