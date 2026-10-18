import pytest

import tomlkit

from tomlkit.items import Key
from tomlkit.items import SingleKey


TEXT = """\
top = 1
dotted.k = 2
[a.b]
x = 1
[c]
[a.d]
y = 2
[t]
inline = {p = 1, q = 2}
"""


@pytest.fixture
def doc():
    return tomlkit.parse(TEXT)


def test_container_contains(doc):
    assert "top" in doc
    assert "missing" not in doc
    assert "dotted" in doc
    assert "c" in doc
    assert "a" in doc  # out-of-order
    assert "x" not in doc


def test_container_contains_key_objects(doc):
    assert SingleKey("top") in doc
    assert SingleKey("nope") not in doc
    assert isinstance(SingleKey("top"), Key)


@pytest.mark.parametrize("bad", [1, None, 1.5, (1,)])
def test_container_contains_non_str_raises_type_error(doc, bad):
    with pytest.raises(TypeError):
        bad in doc


def test_table_contains(doc):
    assert "inline" in doc["t"]
    assert "nope" not in doc["t"]
    assert "k" in doc["dotted"]
    assert "x" in doc["a"]["b"]
    assert "x" not in doc["a"]["d"]


def test_out_of_order_proxy_contains(doc):
    assert "b" in doc["a"]
    assert "d" in doc["a"]
    assert "z" not in doc["a"]


def test_inline_table_contains(doc):
    inline = doc["t"]["inline"]
    assert "p" in inline
    assert "q" in inline
    assert "r" not in inline


def test_contains_after_mutation(doc):
    doc["new"] = 5
    assert "new" in doc
    del doc["new"]
    assert "new" not in doc
    doc["t"]["inline"]["r"] = 3
    assert "r" in doc["t"]["inline"]
    del doc["t"]["inline"]["r"]
    assert "r" not in doc["t"]["inline"]


def test_setitem_overwrites_existing(doc):
    doc["top"] = 99
    assert doc["top"] == 99
    assert doc.as_string().count("top") == 1


def test_built_documents():
    d = tomlkit.document()
    assert "a" not in d
    d["a"] = tomlkit.table()
    d["a"]["x"] = 1
    assert "a" in d
    assert "x" in d["a"]
    assert "y" not in d["a"]
    it = tomlkit.inline_table()
    it["k"] = 1
    assert "k" in it and "z" not in it
