import copy
import pickle
import time

import pytest

from tomlkit import dumps
from tomlkit import parse
from tomlkit.exceptions import ParseError


def test_many_dotted_keys_shared_prefix_parse_fast():
    n = 80
    lines = ["[a]"]
    for i in range(n):
        lines.append(f"b.k{i}.x = {i}")
        lines.append(f"c{i} = {i}")
    text = "\n".join(lines) + "\n"
    start = time.time()
    doc = parse(text)
    assert time.time() - start < 5
    assert doc["a"]["b"][f"k{n - 1}"]["x"] == n - 1
    assert dumps(doc) == text


def test_out_of_order_tables_roundtrip():
    text = "[a.b]\nx = 1\n[c]\ny = 2\n[a.d]\nz = 3\n[a.e]\nw = 4\n"
    doc = parse(text)
    assert dumps(doc) == text
    assert doc["a"]["b"]["x"] == 1
    assert doc["a"]["d"]["z"] == 3
    assert doc["a"]["e"]["w"] == 4


def test_out_of_order_duplicate_leaf_detected():
    text = "[a]\nx = 1\n[c]\n[a.b]\ny = 1\n[d]\n[a.b]\ny = 2\n"
    with pytest.raises(ParseError):
        parse(text)


def test_dotted_key_conflict_detected():
    text = "a.b = 1\nc = 1\na.b = 2\n"
    with pytest.raises(ParseError):
        parse(text)


def test_mutation_after_parse_with_out_of_order():
    text = "[a.b]\nx = 1\n[c]\ny = 2\n[a.d]\nz = 3\n"
    doc = parse(text)
    doc["a"]["b"]["x"] = 10
    doc["a"]["new"] = 5
    del doc["a"]["d"]
    out = dumps(doc)
    again = parse(out)
    assert again["a"]["b"]["x"] == 10
    assert again["a"]["new"] == 5
    assert "d" not in again["a"]
    assert "a" in doc


def test_copy_and_pickle_preserve_out_of_order():
    text = "[a.b]\nx = 1\n[c]\ny = 2\n[a.d]\nz = 3\n"
    doc = parse(text)
    for d in (copy.deepcopy(doc), pickle.loads(pickle.dumps(doc)), doc.unwrap()):
        assert d["a"]["d"]["z"] == 3
    d2 = copy.deepcopy(doc)
    assert dumps(d2) == text
    d2["a"]["e"] = 1
    assert "e" not in doc["a"]
