import time

import tomlkit


def _doc(n):
    return "".join(f"[a.b.c{i}]\nx = {i}\n" for i in range(n))


def test_consecutive_subtables_roundtrip_and_values():
    text = _doc(5)
    doc = tomlkit.parse(text)
    assert doc.as_string() == text
    assert doc.unwrap() == {"a": {"b": {f"c{i}": {"x": i} for i in range(5)}}}


def test_merge_keeps_single_super_table():
    doc = tomlkit.parse(_doc(4))
    assert list(doc["a"]["b"].keys()) == [f"c{i}" for i in range(4)]
    assert len(doc["a"]) == 1


def test_merge_does_not_copy_target():
    doc = tomlkit.parse("[a.b.c]\nx = 1\n")
    b = doc["a"]["b"]
    doc2 = tomlkit.parse("[a.b.c]\nx = 1\n[a.b.d]\ny = 2\n")
    assert doc2["a"]["b"]["d"]["y"] == 2
    assert b is doc["a"]["b"]


def test_out_of_order_tables_still_work_and_not_mutated():
    text = "[a.b]\nx = 1\n[c]\nz = 3\n[a.d]\ny = 2\n"
    doc = tomlkit.parse(text)
    assert doc.as_string() == text
    assert doc["a"]["b"]["x"] == 1
    assert doc["a"]["d"]["y"] == 2
    # repeated access (re-validation) must be stable
    assert doc["a"]["b"]["x"] == 1
    assert doc.unwrap() == {"a": {"b": {"x": 1}, "d": {"y": 2}}, "c": {"z": 3}}
    assert doc.as_string() == text


def test_out_of_order_deeper_shared_super_tables():
    text = "[a.b.c]\n1=1\n[x]\n[a.b.d]\n2=2\n[y]\n[a.e]\n3=3\n"
    doc = tomlkit.parse(text)
    assert doc.as_string() == text
    assert doc.unwrap() == {
        "a": {"b": {"c": {"1": 1}, "d": {"2": 2}}, "e": {"3": 3}},
        "x": {},
        "y": {},
    }


def test_out_of_order_edit_roundtrip():
    doc = tomlkit.parse("[a.b]\nx = 1\n[c]\nz = 3\n[a.d]\ny = 2\n")
    doc["a"]["b"]["x"] = 10
    doc["a"]["d"]["y"] = 20
    out = tomlkit.parse(doc.as_string())
    assert out.unwrap() == {"a": {"b": {"x": 10}, "d": {"y": 20}}, "c": {"z": 3}}


def test_duplicate_still_rejected():
    import pytest

    from tomlkit.exceptions import TOMLKitError

    with pytest.raises(TOMLKitError):
        tomlkit.parse("[a.b.c]\nx=1\n[a.b.c]\ny=2\n")


def test_many_subtables_scales():
    start = time.perf_counter()
    doc = tomlkit.parse(_doc(1500))
    elapsed = time.perf_counter() - start
    assert len(doc["a"]["b"]) == 1500
    assert elapsed < 10
