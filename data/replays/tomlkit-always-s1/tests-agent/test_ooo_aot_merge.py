import tomlkit

DOC = """\
[hooks]
[[hooks.Stop]]
a = 1
[unrelated]
[[hooks.Stop]]
a = 2
[hooks.state]
x = 1
"""


def test_parse_split_aot_does_not_raise():
    doc = tomlkit.parse(DOC)
    assert "Stop" in doc["hooks"]
    assert doc["hooks"]["Stop"] == [{"a": 1}, {"a": 2}]
    assert doc["hooks"]["state"] == {"x": 1}
    assert doc.unwrap() == {
        "hooks": {"Stop": [{"a": 1}, {"a": 2}], "state": {"x": 1}},
        "unrelated": {},
    }


def test_roundtrip_preserved():
    assert tomlkit.parse(DOC).as_string() == DOC


def test_access_does_not_mutate_fragments():
    doc = tomlkit.parse(DOC)
    doc["hooks"]["Stop"]
    assert doc.as_string() == DOC


def test_three_fragments():
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
    doc = tomlkit.parse(text)
    assert [t["a"] for t in doc["hooks"]["Stop"]] == [1, 2, 3]
    assert doc.as_string() == text


def test_edit_element_through_merged_aot():
    doc = tomlkit.parse(DOC)
    doc["hooks"]["Stop"][1]["a"] = 5
    assert doc["hooks"]["Stop"][1]["a"] == 5
    assert "a = 5" in doc.as_string()
    assert "a = 1" in doc.as_string()

