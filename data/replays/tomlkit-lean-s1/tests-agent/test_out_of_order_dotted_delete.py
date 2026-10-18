import tomlkit


def test_delete_dotted_key_in_out_of_order_table():
    content = """\
[a]
b.c = 1
b.d = 2

[z]
q = 1

[a.e]
f = 1
"""
    doc = tomlkit.parse(content)
    del doc["a"]["b"]
    assert "b" not in doc["a"]
    assert tomlkit.parse(doc.as_string()) == {"a": {"e": {"f": 1}}, "z": {"q": 1}}
