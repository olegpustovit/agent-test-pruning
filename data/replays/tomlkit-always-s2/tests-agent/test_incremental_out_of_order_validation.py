import time

import pytest

import tomlkit

from tomlkit.exceptions import TOMLKitError


def test_many_shared_prefix_dotted_keys_parse_fast_and_correct():
    n = 80
    lines = []
    for i in range(n):
        lines.append(f"a.b.c{i} = {i}")
        lines.append(f"x{i} = {i}")
    text = "\n".join(lines) + "\n"
    start = time.perf_counter()
    doc = tomlkit.parse(text)
    assert time.perf_counter() - start < 3
    assert doc.as_string() == text
    assert doc["a"]["b"]["c79"] == 79
    assert len(doc["a"]["b"]) == n


def test_out_of_order_tables_merge():
    text = "[a.b]\nx = 1\n[c]\ny = 2\n[a.d]\nz = 3\n[e]\n[a.f]\nw = 4\n"
    doc = tomlkit.parse(text)
    assert doc.as_string() == text
    assert doc.unwrap() == {
        "a": {"b": {"x": 1}, "d": {"z": 3}, "f": {"w": 4}},
        "c": {"y": 2},
        "e": {},
    }


def test_duplicate_key_in_later_fragment_detected():
    text = "[a.b]\nx = 1\n[c]\n[a.b]\ny = 2\n"
    with pytest.raises(TOMLKitError):
        tomlkit.parse(text)


def test_duplicate_key_in_third_fragment_detected():
    text = "[a]\nx = 1\n[c]\n[a]\ny = 2\n[d]\n[a]\nx = 3\n"
    with pytest.raises(TOMLKitError):
        tomlkit.parse(text)


def test_duplicate_dotted_key_detected():
    text = "a.b = 1\nc = 1\na.d = 2\ne = 1\na.b = 3\n"
    with pytest.raises(TOMLKitError):
        tomlkit.parse(text)


def test_modification_after_parse_revalidates():
    doc = tomlkit.parse("a.b = 1\nc = 1\na.d = 2\n")
    doc["a"]["e"] = 3
    del doc["a"]["b"]
    doc["a"]["b"] = 9
    assert doc.unwrap() == {"a": {"d": 2, "e": 3, "b": 9}, "c": 1}
    out = tomlkit.parse(doc.as_string())
    assert out.unwrap() == doc.unwrap()


def test_remove_out_of_order_key_then_reuse():
    doc = tomlkit.parse("[a.b]\nx=1\n[c]\n[a.d]\ny=2\n")
    del doc["a"]
    assert "a" not in doc
    doc["a"] = {"z": 1}
    assert doc.unwrap()["a"] == {"z": 1}


def test_copy_and_pickle_preserve_out_of_order_keys():
    import copy
    import pickle

    doc = tomlkit.parse("[a.b]\nx=1\n[c]\n[a.d]\ny=2\n")
    for d in (copy.deepcopy(doc), pickle.loads(pickle.dumps(doc))):
        assert d.unwrap() == doc.unwrap()
        d["a"]["q"] = 1
        assert d["a"]["q"] == 1
        assert d._out_of_order_keys


def test_container_unwrap_copy_tracks_out_of_order_keys():
    doc = tomlkit.parse("[a.b]\nx=1\n[c]\n[a.d]\ny=2\n")
    c = doc.copy()
    assert c._out_of_order_keys == doc._out_of_order_keys


def test_validate_returns_container_and_resumes():
    from tomlkit.container import OutOfOrderTableProxy

    doc = tomlkit.parse("[a.b]\nx=1\n[c]\n[a.d]\ny=2\n")
    c = doc
    idx = c._map[tomlkit.items.SingleKey("a")]
    assert isinstance(idx, tuple)
    temp = OutOfOrderTableProxy.validate(c, idx[:1])
    temp = OutOfOrderTableProxy.validate(c, idx[1:], temp)
    assert temp.unwrap() == {"b": {"x": 1}, "d": {"y": 2}}
