from tomlkit import api
from tomlkit.items import DottedKey
from tomlkit.items import SingleKey


def test_key_single_element_list_returns_single_key():
    k = api.key(["foo"])
    assert isinstance(k, SingleKey)
    assert not isinstance(k, DottedKey)
    assert k == api.key("foo")


def test_key_single_element_iterator():
    assert isinstance(api.key(iter(["foo"])), SingleKey)


def test_key_multi_element_still_dotted():
    k = api.key(["foo", "bar"])
    assert isinstance(k, DottedKey)
    assert k.as_string() == "foo.bar"


def test_key_single_list_membership_after_append():
    doc = api.document()
    doc.append(api.key(["foo"]), api.item(1))
    assert "foo" in doc
    assert doc["foo"] == 1
