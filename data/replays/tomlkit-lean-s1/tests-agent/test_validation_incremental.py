import time

import pytest

from tomlkit import parse
from tomlkit.exceptions import ParseError


def test_many_shared_prefix_dotted_keys_parse_fast():
    doc = "".join(f"a.b.k{i} = {i}\n" for i in range(80))
    doc += "[x]\ny = 1\n"
    start = time.time()
    d = parse(doc)
    assert time.time() - start < 5
    assert len(d["a"]["b"]) == 80
    assert d.as_string() == doc


def test_duplicate_detected_after_many_fragments():
    doc = "".join(f"[a.t{i}]\nx = 1\n[o{i}]\n" for i in range(20))
    doc += "[a.t3]\nx = 2\n"
    with pytest.raises(ParseError):
        parse(doc)


def test_duplicate_dotted_key_late_raises():
    doc = "a.b.c = 1\n[x]\ny = 1\n[a.b]\nd = 1\n[a.b]\nc = 2\n"
    with pytest.raises(ParseError):
        parse(doc)


def test_mutation_after_parse_still_validates():
    doc = "[a.b]\nx = 1\n[c]\ny = 1\n[a.d]\nz = 2\n"
    d = parse(doc)
    del d["a"]["b"]
    d["a"]["e"] = 5
    assert d["a"]["d"]["z"] == 2
    assert d["a"]["e"] == 5
    assert "b" not in d["a"]
