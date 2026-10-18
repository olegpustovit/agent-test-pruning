import pytest

import tomlkit


TWO = """\
[hooks]
[[hooks.Stop]]
a = 1
[unrelated]
[[hooks.Stop]]
a = 2
[hooks.state]
"""

THREE = """\
[hooks]
[[hooks.Stop]]
a = 1
[x]
[[hooks.Stop]]
a = 2
[y]
[[hooks.Stop]]
a = 3
[hooks.state]
"""


def test_two_fragments_parse_and_roundtrip():
    doc = tomlkit.parse(TWO)
    assert doc["hooks"]["Stop"].unwrap() == [{"a": 1}, {"a": 2}]
    assert doc.as_string() == TWO
    assert doc.unwrap() == {
        "hooks": {"Stop": [{"a": 1}, {"a": 2}], "state": {}},
        "unrelated": {},
    }


def test_contains_does_not_raise():
    doc = tomlkit.parse(TWO)
    assert "hooks" in doc
    assert "Stop" in doc["hooks"]
    assert "state" in doc["hooks"]


def test_three_fragments():
    doc = tomlkit.parse(THREE)
    assert [t["a"] for t in doc["hooks"]["Stop"]] == [1, 2, 3]
    assert len(doc["hooks"]["Stop"]) == 3
    assert doc.as_string() == THREE


def test_edit_element_through_merged_aot():
    doc = tomlkit.parse(TWO)
    doc["hooks"]["Stop"][1]["a"] = 20
    assert doc.as_string() == TWO.replace("a = 2", "a = 20")
    assert tomlkit.parse(doc.as_string())["hooks"]["Stop"][1]["a"] == 20
