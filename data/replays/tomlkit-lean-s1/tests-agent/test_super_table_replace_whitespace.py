from tomlkit import parse
from tomlkit.container import ends_with_whitespace


def test_replace_super_table_no_extra_blank_line():
    new = parse("[a.b]\nx=2\n\n")["a"]
    doc = parse("[a.b]\nx=1\n\n[c]\ny=1\n")
    doc["a"] = new
    assert doc.as_string() == "[a.b]\nx=2\n\n[c]\ny=1\n"


def test_ends_with_whitespace_nested():
    doc = parse("[a.b]\nx=2\n\n[c]\ny=1\n")
    assert ends_with_whitespace(doc["a"])
    assert not ends_with_whitespace(doc["c"])
