import pytest

import tomlkit

from tomlkit.exceptions import TOMLKitError


DOC = """\
[[fruit]]
name = "apple"

[other]
x = 1

[fruit.apple.texture]
smooth = true
"""


def test_subtable_after_unrelated_table_parses():
    doc = tomlkit.parse(DOC)
    assert doc.unwrap() == {
        "fruit": [{"name": "apple", "apple": {"texture": {"smooth": True}}}],
        "other": {"x": 1},
    }


def test_roundtrip_reparses_to_same_data():
    doc = tomlkit.parse(DOC)
    again = tomlkit.parse(tomlkit.dumps(doc))
    assert again.unwrap() == doc.unwrap()


def test_extends_last_element_only():
    text = """\
[[fruit]]
name = "a"

[[fruit]]
name = "b"

[other]
x = 1

[fruit.physical]
color = "red"
"""
    data = tomlkit.parse(text).unwrap()
    assert data["fruit"][0] == {"name": "a"}
    assert data["fruit"][1] == {"name": "b", "physical": {"color": "red"}}


def test_multiple_subtables_merge():
    text = """\
[[fruit]]
name = "a"

[other]
x = 1

[fruit.p]
c = 1

[fruit.q]
d = 2
"""
    data = tomlkit.parse(text).unwrap()
    assert data["fruit"] == [{"name": "a", "p": {"c": 1}, "q": {"d": 2}}]


def test_contiguous_form_still_works():
    text = '[[fruit]]\nname = "a"\n\n[fruit.p]\nc = 1\n'
    assert tomlkit.parse(text).unwrap() == {"fruit": [{"name": "a", "p": {"c": 1}}]}


def test_plain_table_after_aot_still_conflicts():
    text = '[[fruit]]\nname = "a"\n\n[other]\nx = 1\n\n[fruit]\ny = 2\n'
    with pytest.raises(TOMLKitError):
        tomlkit.parse(text)
