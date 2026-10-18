import pytest

from tomlkit import dumps
from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


DOC = """\
[[fruit]]
name = "apple"

[other]
x = 1

[fruit.apple.texture]
smooth = true
"""


def test_subtable_extends_last_aot_element_after_unrelated_table():
    doc = parse(DOC)
    assert doc.unwrap() == {
        "fruit": [{"name": "apple", "apple": {"texture": {"smooth": True}}}],
        "other": {"x": 1},
    }
    assert parse(dumps(doc)).unwrap() == doc.unwrap()


def test_subtable_extends_only_last_element():
    doc = parse(
        """\
[[fruit]]
name = "a"

[[fruit]]
name = "b"

[other]
x = 1

[fruit.sub]
y = 2
"""
    )
    assert doc["fruit"][0] == {"name": "a"}
    assert doc["fruit"][1] == {"name": "b", "sub": {"y": 2}}


def test_plain_table_after_aot_still_conflicts():
    with pytest.raises(TOMLKitError):
        parse("[[fruit]]\nname = 'a'\n\n[other]\nx = 1\n\n[fruit]\ny = 1\n")
