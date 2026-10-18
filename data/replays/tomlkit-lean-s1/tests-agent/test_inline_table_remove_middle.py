import pytest

import tomlkit


@pytest.mark.parametrize(
    "src, removed, expected",
    [
        ("x = {a = 1, b = 2, c = 3}\n", ["b"], {"a": 1, "c": 3}),
        ("x = {a = 1, b = 2, c = 3, d = 4}\n", ["b", "c"], {"a": 1, "d": 4}),
        ("x = {a = 1, b = 2, c = 3}\n", ["a"], {"b": 2, "c": 3}),
        ("x = {a = 1, b = 2, c = 3}\n", ["c"], {"a": 1, "b": 2}),
    ],
)
def test_remove_inline_table_items_round_trips(src, removed, expected):
    doc = tomlkit.parse(src)
    for k in removed:
        del doc["x"][k]
    out = doc.as_string()
    assert ", ," not in out and ",," not in out
    assert tomlkit.parse(out)["x"] == expected
