import time

import tomlkit


def test_consecutive_subtables_share_super_table_identity():
    doc = tomlkit.parse("[a.b.c]\nx = 1\n[a.b.d]\ny = 2\n[a.b.e]\nz = 3\n")
    assert doc["a"]["b"]["c"]["x"] == 1
    assert doc["a"]["b"]["d"]["y"] == 2
    assert doc["a"]["b"]["e"]["z"] == 3
    assert list(doc["a"]["b"]) == ["c", "d", "e"]


def test_roundtrip_many_subtables():
    text = "".join(f"[a.b.t{i}]\nv = {i}\n\n" for i in range(50))
    doc = tomlkit.parse(text)
    assert doc.as_string() == text
    assert doc["a"]["b"]["t49"]["v"] == 49
    assert len(doc["a"]["b"]) == 50


def test_many_subtables_is_not_quadratic():
    def parse_time(n):
        text = "".join(f"[a.b.t{i}]\nv = {i}\n" for i in range(n))
        start = time.perf_counter()
        tomlkit.parse(text)
        return time.perf_counter() - start

    # Generous bound: the old deep-copy implementation took seconds here.
    assert parse_time(320) < 2.0


def test_out_of_order_tables_roundtrip_and_access():
    text = (
        "[a.b.c]\nx = 1\n[d]\nq = 0\n[a.b.e]\ny = 2\n[a.f]\nz = 3\n"
    )
    doc = tomlkit.parse(text)
    assert doc.as_string() == text
    assert doc["a"]["b"]["c"]["x"] == 1
    assert doc["a"]["b"]["e"]["y"] == 2
    assert doc["a"]["f"]["z"] == 3
    assert doc.unwrap() == {
        "a": {"b": {"c": {"x": 1}, "e": {"y": 2}}, "f": {"z": 3}},
        "d": {"q": 0},
    }


def test_out_of_order_validation_does_not_mutate_live_tables():
    text = "[a.b.c]\nx = 1\n[a.b.d]\ny = 2\n[z]\n[a.b.e]\nw = 3\n[a.g]\nk = 1\n"
    doc = tomlkit.parse(text)
    before = doc.as_string()
    # Repeated access / validation must be stable.
    for _ in range(3):
        assert doc["a"]["b"]["e"]["w"] == 3
        assert doc.as_string() == before
        assert doc.unwrap()["a"]["b"] == {
            "c": {"x": 1},
            "d": {"y": 2},
            "e": {"w": 3},
        }


def test_out_of_order_duplicate_still_detected():
    import pytest

    from tomlkit.exceptions import TOMLKitError

    text = "[a.b.c]\nx = 1\n[z]\n[a.b.c]\ny = 2\n"
    with pytest.raises(TOMLKitError):
        tomlkit.parse(text)


def test_out_of_order_edit_after_parse():
    doc = tomlkit.parse("[a.b.c]\nx = 1\n[z]\n[a.b.d]\ny = 2\n")
    doc["a"]["b"]["d"]["y"] = 5
    doc["a"]["b"]["c"]["x"] = 7
    assert doc.unwrap()["a"]["b"] == {"c": {"x": 7}, "d": {"y": 5}}
    assert "y = 5" in doc.as_string()
