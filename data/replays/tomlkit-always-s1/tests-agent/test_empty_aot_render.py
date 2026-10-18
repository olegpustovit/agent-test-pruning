import pytest

from tomlkit import parse


def _empty(doc, path):
    node = doc
    for p in path:
        node = node[p]
    node.clear()


@pytest.mark.parametrize(
    "src, path, expected",
    [
        ("[[a]]\nx = 1\n", ["a"], "a = []\n"),
        ("[t]\nx = 1\n[[t.a]]\ny = 1\n", ["t", "a"], "[t]\na = []\nx = 1\n"),
        ("[[t.a]]\ny = 1\n", ["t", "a"], "t.a = []\n"),
        (
            "[t]\n[[t.u.a]]\ny = 1\n[t.s]\nz = 1\n",
            ["t", "u", "a"],
            "[t]\nu.a = []\n[t.s]\nz = 1\n",
        ),
    ],
)
def test_emptied_aot_renders_empty_array(src, path, expected):
    doc = parse(src)
    _empty(doc, path)
    out = doc.as_string()
    assert out == expected
    assert parse(out).unwrap() == doc.unwrap()


def test_emptied_aot_hoisted_before_table():
    doc = parse("[t]\nx = 1\n\n[[a]]\ny = 1\n")
    doc["a"].clear()
    out = doc.as_string()
    assert out.startswith("a = []")
    assert parse(out).unwrap() == {"t": {"x": 1}, "a": []}


def test_nonempty_aot_unchanged():
    src = "[[a]]\nx = 1\n[[a]]\nx = 2\n"
    assert parse(src).as_string() == src


def test_emptied_aot_inside_aot_element():
    doc = parse("[[p]]\nn = 1\n[[p.c]]\nm = 1\n")
    doc["p"][0]["c"].clear()
    out = doc.as_string()
    assert parse(out).unwrap() == doc.unwrap() == {"p": [{"n": 1, "c": []}]}
