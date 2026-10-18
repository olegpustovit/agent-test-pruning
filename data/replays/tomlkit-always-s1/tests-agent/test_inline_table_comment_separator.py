import pytest

import tomlkit


@pytest.mark.parametrize(
    "src",
    [
        "a = {\n  x = 1 # c\n}\n",
        "a = {\n  x = 1, # c\n  y = 2 # d\n}\n",
    ],
)
def test_append_after_trailing_comment_roundtrips(src):
    doc = tomlkit.parse(src)
    expected = dict(doc["a"])
    doc["a"]["z"] = 3
    expected["z"] = 3
    out = doc.as_string()
    assert tomlkit.parse(out)["a"] == expected


def test_separator_placed_before_comment():
    doc = tomlkit.parse("a = {\n  x = 1 # c\n}\n")
    doc["a"]["z"] = 3
    out = doc.as_string()
    assert "x = 1, # c" in out
    assert "# c," not in out


def test_existing_trailing_comma_unchanged():
    doc = tomlkit.parse("a = {\n  x = 1, # c\n  y = 2, # d\n}\n")
    doc["a"]["z"] = 3
    out = doc.as_string()
    assert "# d," not in out
    assert tomlkit.parse(out)["a"] == {"x": 1, "y": 2, "z": 3}
