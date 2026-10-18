import tomlkit

from tomlkit.container import ends_with_whitespace
from tomlkit.items import Whitespace


DOC = """\
[a.b]
x = 1

[a.c]
y = 2

[d]
z = 3
"""


def test_ends_with_whitespace_direct():
    assert ends_with_whitespace(Whitespace("\n"))
    assert not ends_with_whitespace(1)


def test_ends_with_whitespace_nested_super_table():
    doc = tomlkit.parse(DOC)
    assert ends_with_whitespace(doc["a"])
    assert not ends_with_whitespace(doc["d"])


def test_ends_with_whitespace_empty_table():
    assert not ends_with_whitespace(tomlkit.table())


def test_ends_with_whitespace_aot():
    doc = tomlkit.parse("[[t]]\na = 1\n\n[[t]]\na = 2\n")
    assert ends_with_whitespace(doc["t"][0])


def test_replace_super_table_preserves_blank_line():
    doc = tomlkit.parse(DOC)
    new = tomlkit.table()
    new.add("k", 1)
    doc["a"] = new
    out = doc.as_string()
    assert "[d]" in out
    assert "\n\n[d]" in out
    assert tomlkit.parse(out)["d"]["z"] == 3
    assert tomlkit.parse(out)["a"]["k"] == 1
