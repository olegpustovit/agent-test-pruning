import pytest

from tomlkit import parse


@pytest.mark.parametrize(
    "src, removed, expected",
    [
        ("t = {a = 1, b = 2, c = 3}", ["b"], {"a": 1, "c": 3}),
        ("t = {a = 1, b = 2, c = 3, d = 4}", ["b"], {"a": 1, "c": 3, "d": 4}),
        ("t = {a = 1, b = 2, c = 3, d = 4}", ["c"], {"a": 1, "b": 2, "d": 4}),
        ("t = {a = 1, b = 2, c = 3, d = 4}", ["b", "c"], {"a": 1, "d": 4}),
        ("t = {a=1,b=2,c=3}", ["b"], {"a": 1, "c": 3}),
        ("t = {a = 1, b = 2, c = 3}", ["a"], {"b": 2, "c": 3}),
        ("t = {a = 1, b = 2, c = 3}", ["c"], {"a": 1, "b": 2}),
    ],
)
def test_remove_inline_table_key_roundtrips(src, removed, expected):
    doc = parse(src)
    for key in removed:
        del doc["t"][key]
    out = doc.as_string()
    assert ",," not in out.replace(" ", "")
    assert parse(out)["t"] == expected


def test_remove_middle_keeps_neighbors_formatting():
    doc = parse("t = {a = 1, b = 2, c = 3}")
    del doc["t"]["b"]
    assert doc.as_string().count(",") == 1
