import pytest

import tomlkit


@pytest.mark.parametrize(
    "text",
    [
        "[a]\nx=1\n[a . 'b']\ny=1\n",
        "[a]\n[ a . b ]\ny=1\n",
        "[ a ]\n[ a . b ]\ny=1\n",
    ],
)
def test_self_assignment_of_parent_preserves_display_name(text):
    doc = tomlkit.parse(text)
    doc["a"] = doc["a"]
    assert doc.as_string() == text


def test_self_assignment_of_child_preserves_display_name():
    text = "[a]\nx=1\n[a . 'b']\ny=1\n"
    doc = tomlkit.parse(text)
    doc["a"]["b"] = doc["a"]["b"]
    assert doc.as_string() == text


def test_assigning_a_different_table_still_invalidates_display_name():
    doc = tomlkit.parse("[a]\nx=1\n")
    other = tomlkit.parse("[ b ]\ny = 2\n")["b"]
    assert other.display_name == " b "
    doc["a"] = other
    assert other.display_name is None
