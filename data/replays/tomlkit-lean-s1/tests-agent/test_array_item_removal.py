import pytest

import tomlkit


@pytest.mark.parametrize(
    "src, idx, expected",
    [
        ("a = [1, 2, 3]", 1, "a = [1, 3]"),
        ("a = [1, 2, 3]", 0, "a = [2, 3]"),
        ("a = [1, 2, 3]", 2, "a = [1, 2]"),
        ("a = [\n  1,\n  2,\n  3,\n]", 1, "a = [\n  1,\n  3,\n]"),
        (
            "a = [\n  1, # c1\n  2, # c2\n  3, # c3\n]",
            1,
            "a = [\n  1, # c1\n  3, # c3\n]",
        ),
        ("a = [1, 2,\n 3]", 1, "a = [1,\n 3]"),
        ("a = [1 , 2 , 3]", 1, "a = [1 , 3]"),
    ],
)
def test_array_item_removal_keeps_valid_toml(src, idx, expected):
    doc = tomlkit.parse(src)
    del doc["a"][idx]
    out = doc.as_string()
    assert out == expected
    assert tomlkit.parse(out)["a"] == doc["a"]


def test_parse_roundtrip_array_with_space_before_comma():
    src = "a = [1 , 2 ,\n  3 ]"
    assert tomlkit.parse(src).as_string() == src
