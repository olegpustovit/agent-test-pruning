from tomlkit import aot
from tomlkit import parse
from tomlkit import table


def _make_aot():
    a = aot()
    t = table()
    t["x"] = 1
    a.append(t)
    return a


def test_replace_dotted_key_with_aot_keeps_following_sibling() -> None:
    # https://github.com/python-poetry/tomlkit/issues/542
    doc = parse("a.b = 1\nc.d = 2\n")
    doc["a"] = _make_aot()
    out = doc.as_string()
    assert out.index("c.d = 2") < out.index("[[a]]")
    assert parse(out) == {"c": {"d": 2}, "a": [{"x": 1}]}


def test_replace_dotted_key_with_aot_last_key() -> None:
    doc = parse("c.d = 2\na.b = 1\n")
    doc["a"] = _make_aot()
    assert parse(doc.as_string()) == {"c": {"d": 2}, "a": [{"x": 1}]}


def test_replace_dotted_key_with_aot_multiple_siblings() -> None:
    doc = parse("a.b = 1\nc.d = 2\ne = 3\nf.g = 4\n")
    doc["a"] = _make_aot()
    assert parse(doc.as_string()) == {
        "c": {"d": 2},
        "e": 3,
        "f": {"g": 4},
        "a": [{"x": 1}],
    }
