import pytest

from tomlkit import parse


CASES = [
    "[[a]]\nx = 1\n",
    "[t]\nk = 1\n[[t.a]]\nx = 1\n",
    "[[t.a]]\nx = 1\n",
    "[t]\nk = 1\n[[t.u.a]]\nx = 1\n",
    "[t]\n[[t.a]]\nx = 1\n[t.s]\ny = 1\n",
    "[t]\n[t.s]\ny = 1\n[[t.a]]\nx = 1\n",
    "[[t]]\n[[t.a]]\nx = 1\n",
    "[t.s]\ny = 1\n[[a]]\nx = 1\n",
    "[t]\nk = 1\n[[t.u.v.a]]\nx = 1\n",
]


def _empty(doc):
    def walk(c):
        for k in list(c.keys()):
            v = c[k]
            if hasattr(v, "body") and type(v).__name__ == "AoT":
                for el in list(v):
                    walk(el)
                while len(v):
                    v.pop() if hasattr(v, "pop") else v.__delitem__(-1)
            elif isinstance(v, dict):
                walk(v)

    walk(doc)


def test_empty_aot_top_level_rendered():
    doc = parse("[[a]]\nx = 1\n")
    del doc["a"][0]
    assert doc.as_string() == "a = []\n"


@pytest.mark.parametrize("src", CASES)
def test_empty_aot_roundtrip(src):
    doc = parse(src)
    _empty(doc)
    out = doc.as_string()
    assert parse(out).unwrap() == doc.unwrap()


def test_empty_aot_hoisted_before_table():
    doc = parse("[t]\nk = 1\n\n[[a]]\nx = 1\n")
    del doc["a"][0]
    out = doc.as_string()
    assert parse(out).unwrap() == {"t": {"k": 1}, "a": []}
    assert out.index("a = []") < out.index("[t]")
