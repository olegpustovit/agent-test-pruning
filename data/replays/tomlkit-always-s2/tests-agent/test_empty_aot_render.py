import pytest

from tomlkit import parse


def _empty(doc, *path):
    cur = doc
    for p in path:
        cur = cur[p]
    cur.clear()


@pytest.mark.parametrize(
    "src, path",
    [
        ("[[t]]\nx = 1\n", ("t",)),
        ("[x]\ny = 1\n[[t]]\nx = 1\n", ("t",)),
        ("[t]\n[[t.a]]\nx = 1\n", ("t", "a")),
        ("[t]\nk = 1\n[[t.a]]\nx = 1\n", ("t", "a")),
        ("[t]\n[[t.a]]\nx = 1\n[t.s]\nz = 1\n", ("t", "a")),
        ("[t]\n[t.s]\nz = 1\n[[t.a]]\nx = 1\n", ("t", "a")),
        ("[t.u]\nq = 1\n[[t.u.a]]\nx = 1\n", ("t", "u", "a")),
        ("[t]\nk = 1\n[t.u]\n[[t.u.a]]\nx = 1\n", ("t", "u", "a")),
        ("[[t.a]]\nx = 1\n", ("t", "a")),
        ("[[t]]\nn = 1\n[[t.a]]\nx = 1\n", ("t", 0, "a")),
    ],
)
def test_emptied_aot_roundtrip(src, path):
    doc = parse(src)
    _empty(doc, *path)
    out = doc.as_string()
    assert parse(out).unwrap() == doc.unwrap()


def test_emptied_aot_rendered_inline():
    doc = parse("[x]\ny = 1\n[[t]]\nx = 1\n")
    doc["t"].clear()
    assert doc.as_string() == "t = []\n[x]\ny = 1\n"


def test_nonempty_aot_unchanged():
    src = "[x]\ny = 1\n[[t]]\nx = 1\n"
    assert parse(src).as_string() == src
