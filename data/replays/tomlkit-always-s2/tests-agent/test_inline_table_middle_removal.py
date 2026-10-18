import pytest

import tomlkit


@pytest.mark.parametrize(
    "src",
    [
        "t = {a = 1, b = 2, c = 3}",
        "t = {a = 1, b = 2, c = 3, d = 4}",
        "t = {a=1,b=2,c=3}",
    ],
)
@pytest.mark.parametrize("key", ["a", "b", "c"])
def test_remove_inline_table_key_roundtrips(src, key):
    doc = tomlkit.parse(src)
    expected = {k: v for k, v in doc["t"].items() if k != key}
    del doc["t"][key]
    out = doc.as_string()
    assert ", ," not in out
    assert ",," not in out
    assert tomlkit.parse(out)["t"] == expected


def test_remove_middle_no_duplicate_comma():
    doc = tomlkit.parse("t = {a = 1, b = 2, c = 3}")
    del doc["t"]["b"]
    assert doc.as_string().count(",") == 1
    assert tomlkit.parse(doc.as_string()) == {"t": {"a": 1, "c": 3}}


def test_remove_two_middle_keys():
    doc = tomlkit.parse("t = {a = 1, b = 2, c = 3, d = 4}")
    del doc["t"]["b"]
    del doc["t"]["c"]
    assert tomlkit.parse(doc.as_string()) == {"t": {"a": 1, "d": 4}}
