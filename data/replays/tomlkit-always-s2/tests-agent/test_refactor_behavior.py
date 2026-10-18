import pytest

import tomlkit
from tomlkit.exceptions import ParseError


def test_all_exports_resolve_and_sorted():
    assert len(set(tomlkit.__all__)) == len(tomlkit.__all__)
    for name in tomlkit.__all__:
        assert hasattr(tomlkit, name)
    for name in ("TOMLDocument", "register_encoder", "unregister_encoder"):
        assert name in tomlkit.__all__


def test_array_as_string_roundtrip():
    doc = tomlkit.parse("a = [1, 2,3]\nb = []\n")
    assert doc.as_string() == "a = [1, 2,3]\nb = []\n"
    doc["a"].append(4)
    assert doc["a"].as_string() == "[1, 2,3, 4]"


def test_inline_table_dotted_key_output():
    src = "t = {a.b = 1, c = 2}\n"
    assert tomlkit.parse(src).as_string() == src


def test_array_add_line():
    arr = tomlkit.array()
    arr.add_line(1, 2)
    arr.add_line(3)
    assert list(arr) == [1, 2, 3]
    with pytest.raises(ValueError):
        arr.add_line(tomlkit.comment("x"))


def test_comment_control_char_rejected():
    with pytest.raises(ParseError):
        tomlkit.parse("a = 1 # bad\x01\n")
    with pytest.raises(ParseError):
        tomlkit.parse("a = 1 # bad\x7f\n")
    assert tomlkit.parse("a = 1 # tab\there\n")["a"] == 1


def test_string_control_chars():
    with pytest.raises(ParseError):
        tomlkit.parse('a = "x\x01"\n')
    with pytest.raises(ParseError):
        tomlkit.parse('a = "x\x7f"\n')
    assert tomlkit.parse('a = "x\ty"\n')["a"] == "x\ty"
    with pytest.raises(ParseError):
        tomlkit.parse('a = """x\x01"""\n')


def test_inline_table_commas():
    assert tomlkit.parse("t = {a = 1, b = 2}")["t"] == {"a": 1, "b": 2}
    for bad in ("t = {a = 1 b = 2}", "t = {, a = 1}", "t = {a = 1,, b = 2}"):
        with pytest.raises(ParseError):
            tomlkit.parse(bad)


def test_number_parsing_edge_cases():
    d = tomlkit.parse("a = 0.5\nb = 0e1\nc = 0x1F\nd = 0o7\ne = 0b1\nf = -0.5\ng = 1e2\n")
    assert d["a"] == 0.5 and d["c"] == 31 and d["d"] == 7 and d["e"] == 1
    assert d["f"] == -0.5 and d["g"] == 100.0
    for bad in ("a = 01", "a = +.5", "a = 1.", "a = 1.e2", "a = -.5", "a = 1_"):
        with pytest.raises(ParseError):
            tomlkit.parse(bad)
