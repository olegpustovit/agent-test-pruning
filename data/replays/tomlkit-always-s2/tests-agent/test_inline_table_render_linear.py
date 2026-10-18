import time

import pytest

import tomlkit


@pytest.mark.parametrize(
    "src, deleted, expected",
    [
        ("a = {x = 1, y = 2, z = 3}", ["z"], "a = {x = 1, y = 2}"),
        ("a = {x = 1, y = 2, z = 3}", ["x"], "a = {y = 2, z = 3}"),
        ("a = {x = 1, y = 2, z = 3}", ["y"], "a = {x = 1, z = 3}"),
        ("a = {x = 1, y = 2, z = 3}", ["y", "z"], "a = {x = 1}"),
        ("a = {x = 1, y = 2, z = 3}", ["x", "z"], "a = {y = 2}"),
        ("a = {x = 1, y = 2, z = 3}", ["x", "y", "z"], "a = {}"),
    ],
)
def test_delete_keys_no_dangling_or_double_separator(src, deleted, expected):
    doc = tomlkit.parse(src)
    for k in deleted:
        del doc["a"][k]
    out = doc.as_string()
    assert out.replace(" ", "") == expected.replace(" ", "")
    assert tomlkit.parse(out).unwrap() == doc.unwrap()


def test_add_after_delete_roundtrips():
    doc = tomlkit.parse("a = {x = 1, y = 2, z = 3}")
    del doc["a"]["z"]
    doc["a"]["w"] = 4
    out = doc.as_string()
    assert tomlkit.parse(out).unwrap() == {"a": {"x": 1, "y": 2, "w": 4}}


def test_unmodified_inline_table_roundtrip_preserved():
    src = "a = {x = 1 , y = 2,  z = 3 , }\nb = { p = 1, q = 2 }\n"
    assert tomlkit.parse(src).as_string() == src


def test_large_inline_table_delete_and_render():
    n = 2000
    src = "a = {" + ", ".join(f"k{i} = {i}" for i in range(n)) + "}"
    doc = tomlkit.parse(src)
    assert doc.as_string() == src
    for i in range(0, n, 2):
        del doc["a"][f"k{i}"]
    del doc["a"][f"k{n - 1}"]
    out = doc.as_string()
    assert tomlkit.parse(out).unwrap() == {
        "a": {f"k{i}": i for i in range(1, n - 1, 2)}
    }


def test_large_inline_table_render_is_not_quadratic():
    def render_time(n):
        src = "a = {" + ", ".join(f"k{i} = {i}" for i in range(n)) + "}"
        doc = tomlkit.parse(src)
        best = float("inf")
        for _ in range(3):
            t = time.perf_counter()
            doc.as_string()
            best = min(best, time.perf_counter() - t)
        return best

    small, large = render_time(500), render_time(4000)
    # 8x the keys: linear ~8x, quadratic ~64x.
    assert large < small * 30
