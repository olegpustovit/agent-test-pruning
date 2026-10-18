import pytest

import tomlkit


DOC = """\
[tool.a]
x = 1

# comment

[other]
y = 2

[tool.b]
z = 3


[tool.a.sub]
w = 4

# trailing

"""


def test_tables_map_indices_unique():
    doc = tomlkit.parse(DOC)
    tool = doc["tool"]
    assert type(tool).__name__ == "OutOfOrderTableProxy"
    assert tool._tables_map
    for indices in tool._tables_map.values():
        assert len(indices) == len(set(indices))


def test_repeated_blank_entries_map_to_table_once():
    doc = tomlkit.parse("[a]\nx = 1\n\n\ny = 2\n\n[o]\n[a.c]\nq = 1\n")
    a = doc["a"]
    assert type(a).__name__ == "OutOfOrderTableProxy"
    assert a._tables_map[None] == [0]


def test_delete_from_out_of_order_table():
    doc = tomlkit.parse(DOC)
    tool = doc["tool"]
    del tool["b"]
    assert "b" not in tool
    reparsed = tomlkit.parse(doc.as_string())
    assert reparsed["tool"] == {"a": {"x": 1, "sub": {"w": 4}}}


def test_delete_missing_key_raises():
    doc = tomlkit.parse(DOC)
    with pytest.raises(tomlkit.exceptions.NonExistentKey):
        del doc["tool"]["missing"]
