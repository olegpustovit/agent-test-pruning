import pytest

from tomlkit import parse
from tomlkit.items import SingleKey

DOC = """\
a = 1
[x]
y = 2
[x.z]
w = 3
dotted.k = 4
inl = {p = 1, q = {r = 2}}
"""

OOO = """\
[a.b]
c = 1
[d]
e = 1
[a.f]
g = 2
"""


def test_container_contains():
    doc = parse(DOC)
    assert "a" in doc
    assert "x" in doc
    assert "missing" not in doc
    assert SingleKey("a") in doc
    assert "dotted" in doc["x"]["z"]
    assert "k" in doc["x"]["z"]["dotted"]


def test_container_contains_type_error():
    doc = parse(DOC)
    with pytest.raises(TypeError):
        1 in doc  # noqa: B015


def test_table_contains():
    doc = parse(DOC)
    assert "y" in doc["x"]
    assert "z" in doc["x"]
    assert "nope" not in doc["x"]
    assert "a" not in doc["x"]


def test_inline_table_contains():
    doc = parse(DOC)
    inl = doc["x"]["z"]["inl"]
    assert "p" in inl
    assert "q" in inl
    assert "r" not in inl
    assert "r" in inl["q"]


def test_out_of_order_contains():
    doc = parse(OOO)
    assert "a" in doc
    assert "d" in doc
    assert "b" in doc["a"]
    assert "f" in doc["a"]
    assert "zz" not in doc["a"]
    assert "c" in doc["a"]["b"]


def test_contains_after_mutation():
    doc = parse(DOC)
    del doc["a"]
    assert "a" not in doc
    doc["n"] = 5
    assert "n" in doc
    doc["x"]["new"] = 1
    assert "new" in doc["x"]
    # setitem on existing key still detects presence
    doc["n"] = 6
    assert doc["n"] == 6
