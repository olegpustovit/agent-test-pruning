import pytest

from tomlkit import dumps
from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


def test_dotted_key_extends_implicit_super_table() -> None:
    text = "[a.b.c]\n[a]\nb.z = 1\n"
    doc = parse(text)
    assert doc == {"a": {"b": {"c": {}, "z": 1}}}
    assert dumps(doc) == text


def test_dotted_key_extends_super_table_with_values() -> None:
    text = "[a.b.c]\nx = 1\n[a]\nb.z = 2\n"
    doc = parse(text)
    assert doc == {"a": {"b": {"c": {"x": 1}, "z": 2}}}
    assert dumps(doc) == text


def test_dotted_key_on_concrete_table_still_rejected() -> None:
    with pytest.raises(TOMLKitError):
        parse("[a.b]\n[a]\nb.z = 1\n")


def test_dotted_key_redefining_subtable_of_super_table_rejected() -> None:
    with pytest.raises(TOMLKitError):
        parse("[a.b.c]\n[a]\nb.c.d = 1\n")
