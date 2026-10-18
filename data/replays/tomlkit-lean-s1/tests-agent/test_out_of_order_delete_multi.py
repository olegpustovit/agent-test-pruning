import tomlkit


def test_delete_key_present_in_multiple_out_of_order_parts():
    content = """\
[a.b]
x = 1

[c]
y = 1

[a.b.d]
z = 1

[a]
q = 1
"""
    doc = tomlkit.parse(content)
    del doc["a"]["b"]
    assert "b" not in doc["a"]
    out = doc.as_string()
    assert "[a.b" not in out
    assert tomlkit.parse(out) == {"a": {"q": 1}, "c": {"y": 1}}
