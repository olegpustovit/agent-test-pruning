import pytest

import tomlkit

from tomlkit.exceptions import TOMLKitError


def test_dotted_key_extends_implicit_super_table() -> None:
    text = "[a.b.c]\n\n[a]\nb.z = 1\n"
    doc = tomlkit.parse(text)
    assert doc == {"a": {"b": {"c": {}, "z": 1}}}
    assert doc.as_string() == text
    assert tomlkit.parse(doc.as_string()) == doc


def test_dotted_key_extends_super_table_with_values() -> None:
    text = "[a.b.c]\nx = 1\n\n[a]\nb.z = 2\n"
    doc = tomlkit.parse(text)
    assert doc == {"a": {"b": {"c": {"x": 1}, "z": 2}}}
    assert doc.as_string() == text


def test_dotted_key_redefining_subtable_still_rejected() -> None:
    with pytest.raises(TOMLKitError):
        tomlkit.parse("[a.b.c]\n\n[a]\nb.c.d = 1\n")


def test_dotted_key_on_concrete_table_still_rejected() -> None:
    with pytest.raises(TOMLKitError):
        tomlkit.parse("[a.b]\n\n[a]\nb.z = 1\n")
