import pytest

import tomlkit

from tomlkit.exceptions import TOMLKitError


DOC = """\
[[fruit]]
name = "apple"

[other]
a = 1

[fruit.apple.texture]
smooth = true
"""


def test_subtable_after_unrelated_table_extends_last_aot_element():
    doc = tomlkit.parse(DOC)
    assert doc.unwrap() == {
        "fruit": [{"name": "apple", "apple": {"texture": {"smooth": True}}}],
        "other": {"a": 1},
    }


def test_extends_only_last_element():
    doc = tomlkit.parse(
        '[[fruit]]\nname = "a"\n\n[[fruit]]\nname = "b"\n\n[other]\nx = 1\n\n'
        "[fruit.sub]\ny = 2\n"
    )
    assert doc.unwrap()["fruit"] == [{"name": "a"}, {"name": "b", "sub": {"y": 2}}]


def test_roundtrip_reparses_to_same_data():
    doc = tomlkit.parse(DOC)
    again = tomlkit.parse(doc.as_string())
    assert again.unwrap() == doc.unwrap()


def test_non_super_table_after_aot_still_conflicts():
    with pytest.raises(TOMLKitError):
        tomlkit.parse('[[fruit]]\nname = "a"\n\n[other]\na = 1\n\n[fruit]\nb = 1\n')


def test_contiguous_form_still_works():
    doc = tomlkit.parse('[[fruit]]\nname = "a"\n\n[fruit.apple.texture]\nsmooth = true\n')
    assert doc.unwrap() == {
        "fruit": [{"name": "a", "apple": {"texture": {"smooth": True}}}]
    }
