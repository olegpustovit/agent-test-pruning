import tomlkit

from tomlkit.items import DottedKey
from tomlkit.items import SingleKey


def test_single_element_list_returns_single_key():
    k = tomlkit.key(["a"])
    assert isinstance(k, SingleKey)
    assert not isinstance(k, DottedKey)
    assert k.key == "a"


def test_single_element_iterator_returns_single_key():
    assert isinstance(tomlkit.key(iter(["a"])), SingleKey)


def test_multi_element_list_still_dotted():
    k = tomlkit.key(["a", "b"])
    assert isinstance(k, DottedKey)


def test_single_element_key_append_contains():
    doc = tomlkit.document()
    doc.append(tomlkit.key(["a"]), 1)
    assert "a" in doc
    assert doc["a"] == 1
    assert tomlkit.dumps(doc) == "a = 1\n"
