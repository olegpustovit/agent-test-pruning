import pytest

import tomlkit


@pytest.mark.parametrize(
    "src, path, expected",
    [
        ("a = {b.c = 1, x = 5}\n", ["a", "b"], {"a": {"b": {"c": 1, "e": 3}, "x": 5}}),
        ("a = {b.c.d = 1}\n", ["a", "b", "c"], {"a": {"b": {"c": {"d": 1, "e": 3}}}}),
        (
            "a = {b.c = 1, b.d = 2}\n",
            ["a", "b"],
            {"a": {"b": {"c": 1, "d": 2, "e": 3}}},
        ),
    ],
)
def test_add_to_dotted_key_in_inline_table(src, path, expected):
    doc = tomlkit.parse(src)
    target = doc
    for p in path:
        target = target[p]
    target["e"] = 3
    out = doc.as_string()
    assert tomlkit.parse(out) == expected
    assert "b.e = 3" in out or "c.e = 3" in out


def test_unmodified_roundtrip_preserved():
    src = "a = {b.c = 1, b.d = 2, x = 5}\n"
    assert tomlkit.parse(src).as_string() == src
