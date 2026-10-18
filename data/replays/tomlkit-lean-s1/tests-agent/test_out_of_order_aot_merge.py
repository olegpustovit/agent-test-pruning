from tomlkit import dumps
from tomlkit import parse


def test_aot_split_across_out_of_order_parts():
    text = """\
[hooks]
[[hooks.Stop]]
a = 1
[unrelated]
[[hooks.Stop]]
a = 2
[hooks.state]
x = 1
"""
    doc = parse(text)
    assert "state" in doc["hooks"]
    assert [t["a"] for t in doc["hooks"]["Stop"]] == [1, 2]
    assert doc["hooks"].unwrap() == {"Stop": [{"a": 1}, {"a": 2}], "state": {"x": 1}}
    assert dumps(doc) == text


def test_aot_split_across_three_parts():
    text = """\
[hooks]
[[hooks.Stop]]
a = 1
[u1]
[[hooks.Stop]]
a = 2
[u2]
[[hooks.Stop]]
a = 3
[hooks.state]
"""
    doc = parse(text)
    assert [t["a"] for t in doc["hooks"]["Stop"]] == [1, 2, 3]
    assert dumps(doc) == text
