from tomlkit import aot
from tomlkit import parse
from tomlkit import table


def _make_aot():
    a = aot()
    t = table()
    t["x"] = 9
    a.append(t)
    return a


def test_replace_dotted_key_with_aot_keeps_following_sibling() -> None:
    doc = parse("a.b = 1\nc.d = 2\n")
    doc["a"] = _make_aot()
    out = doc.as_string()
    assert out.index("c.d = 2") < out.index("[[a]]")
    assert parse(out) == {"c": {"d": 2}, "a": [{"x": 9}]}


def test_replace_dotted_key_with_aot_alone() -> None:
    doc = parse("a.b = 1\n")
    doc["a"] = _make_aot()
    assert parse(doc.as_string()) == {"a": [{"x": 9}]}
    assert "a.b" not in doc.as_string()


def test_replace_dotted_key_with_aot_keeps_preceding_and_plain_siblings() -> None:
    doc = parse("z = 0\na.b = 1\nc.d = 2\ne = 3\n")
    doc["a"] = _make_aot()
    assert parse(doc.as_string()) == {
        "z": 0,
        "c": {"d": 2},
        "e": 3,
        "a": [{"x": 9}],
    }
