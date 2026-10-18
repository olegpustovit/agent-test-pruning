import tomlkit

from tomlkit.items import DottedKey
from tomlkit.items import SingleKey


def test_single_element_list_returns_single_key():
    k = tomlkit.key(["foo"])
    assert isinstance(k, SingleKey)
    assert not isinstance(k, DottedKey)
    assert k.key == "foo"


def test_single_element_generator_returns_single_key():
    k = tomlkit.key(x for x in ["foo"])
    assert isinstance(k, SingleKey)


def test_multi_element_list_returns_dotted_key():
    k = tomlkit.key(["a", "b"])
    assert isinstance(k, DottedKey)
    assert k.as_string() == "a.b"


def test_str_returns_single_key():
    assert isinstance(tomlkit.key("foo"), SingleKey)


def test_membership_after_append_single_element_list():
    doc = tomlkit.document()
    doc.append(tomlkit.key(["foo"]), tomlkit.item(1))
    assert "foo" in doc
    assert doc["foo"] == 1
    assert tomlkit.dumps(doc) == "foo = 1\n"
