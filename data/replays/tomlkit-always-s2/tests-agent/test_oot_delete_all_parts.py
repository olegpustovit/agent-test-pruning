import pytest

import tomlkit

from tomlkit.exceptions import NonExistentKey


# Table "a" is split in three parts; sub-table "b" appears in two of them.
DOC = """\
[a.b]
k = 1

[c]
y = 1

[a.b.e]
k = 2

[a.f]
q = 1
"""


def test_delete_key_spanning_parts_removes_all():
    doc = tomlkit.parse(DOC)
    del doc["a"]["b"]
    assert "b" not in doc["a"]
    out = doc.as_string()
    assert "[a.b" not in out
    assert tomlkit.parse(out) == {"a": {"f": {"q": 1}}, "c": {"y": 1}}


def test_delete_missing_key_raises():
    doc = tomlkit.parse(DOC)
    with pytest.raises(NonExistentKey):
        del doc["a"]["nope"]


def test_setitem_key_spanning_parts_overwrites_and_removes_others():
    doc = tomlkit.parse("[a.b]\nk = 1\n[c]\ny = 1\n[a.b.e]\nk = 2\n")
    doc["a"]["b"] = {"n": 5}
    out = doc.as_string()
    assert tomlkit.parse(out) == {"a": {"b": {"n": 5}}, "c": {"y": 1}}
    assert "[a.b.e]" not in out
