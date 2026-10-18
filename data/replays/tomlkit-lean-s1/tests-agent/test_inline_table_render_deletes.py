import pytest

from tomlkit import dumps
from tomlkit import parse


@pytest.mark.parametrize(
    ("src", "delete", "expected"),
    [
        ("{a = 1, b = 2, c = 3}", ["c"], "{a = 1, b = 2}"),
        ("{a = 1, b = 2, c = 3}", ["b", "c"], "{a = 1}"),
        ("{a = 1, b = 2, c = 3}", ["a"], "{b = 2, c = 3}"),
        ("{a = 1, b = 2, c = 3}", ["a", "c"], "{b = 2}"),
        ("{a = 1, b = 2, c = 3}", ["a", "b", "c"], "{}"),
    ],
)
def test_inline_table_delete_render(src, delete, expected):
    doc = parse(f"t = {src}\n")
    for k in delete:
        del doc["t"][k]
    assert dumps(doc).replace(" ", "") == f"t = {expected}\n".replace(" ", "")
    assert parse(dumps(doc)) == {"t": {k: v for k, v in parse(f"t = {src}")["t"].items() if k not in delete}}


def test_large_inline_table_roundtrip_and_delete():
    n = 500
    src = "t = {" + ", ".join(f"k{i} = {i}" for i in range(n)) + "}\n"
    doc = parse(src)
    assert dumps(doc) == src
    del doc["t"][f"k{n - 1}"]
    del doc["t"]["k0"]
    out = dumps(doc)
    assert parse(out)["t"] == {f"k{i}": i for i in range(1, n - 1)}
    assert ",}" not in out.replace(" ", "")
