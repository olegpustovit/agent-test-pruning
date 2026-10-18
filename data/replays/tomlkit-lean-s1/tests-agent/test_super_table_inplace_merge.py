from __future__ import annotations

import pytest

from tomlkit import dumps
from tomlkit import parse


def test_many_sibling_subtables_share_super_table() -> None:
    n = 200
    text = "".join(f"[a.b.c{i}]\nx = {i}\n\n" for i in range(n))
    doc = parse(text)
    assert dumps(doc) == text
    assert len(doc["a"]["b"]) == n
    assert doc["a"]["b"]["c0"]["x"] == 0
    assert doc["a"]["b"][f"c{n - 1}"]["x"] == n - 1
    assert doc.unwrap() == {"a": {"b": {f"c{i}": {"x": i} for i in range(n)}}}


def test_out_of_order_tables_are_not_mutated_by_validation() -> None:
    text = """\
[a.b.c]
x = 1

[d]
y = 2

[a.b.e]
z = 3

[a.f]
w = 4
"""
    doc = parse(text)
    assert dumps(doc) == text
    # Repeated access re-runs validation; results must stay stable.
    for _ in range(3):
        assert doc["a"]["b"]["c"]["x"] == 1
        assert doc["a"]["b"]["e"]["z"] == 3
        assert doc["a"]["f"]["w"] == 4
        assert doc.unwrap() == {
            "a": {"b": {"c": {"x": 1}, "e": {"z": 3}}, "f": {"w": 4}},
            "d": {"y": 2},
        }
    assert dumps(doc) == text


def test_out_of_order_duplicate_still_detected() -> None:
    from tomlkit.exceptions import TOMLKitError

    text = "[a.b]\nx = 1\n\n[d]\n\n[a.b]\ny = 2\n"
    with pytest.raises(TOMLKitError):
        parse(text)
