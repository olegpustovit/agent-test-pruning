import pytest

import tomlkit


@pytest.mark.parametrize(
    "text",
    [
        "a = {x = 1, y = 2 , }\n",
        "a = {x = 1,\n  y = 2,\n}\n",
        "a = {x = 1, y = 2}\n",
        "a = {x = 1,\n  y = 2\n}\n",
    ],
)
def test_append_keeps_valid_separator(text):
    doc = tomlkit.parse(text)
    doc["a"].append("z", 3)
    out = doc.as_string()
    assert tomlkit.parse(out)["a"] == {"x": 1, "y": 2, "z": 3}


def test_append_with_explicit_commas_exact():
    doc = tomlkit.parse("a = {x = 1, y = 2 , }\n")
    doc["a"].append("z", 3)
    assert doc.as_string() == "a = {x = 1, y = 2 ,  z = 3}\n"


@pytest.mark.parametrize(
    "text",
    [
        "t = {\n  a = 1, # c\n  b = 2 # d\n}\n",
        "t = {\n  a = 1,\n  b = 2 # d\n}\n",
    ],
)
def test_append_after_trailing_comment_roundtrips(text):
    doc = tomlkit.parse(text)
    doc["t"]["z"] = 3
    out = doc.as_string()
    assert "# d," not in out
    assert tomlkit.parse(out)["t"] == {"a": 1, "b": 2, "z": 3}
    assert "b = 2, # d" in out
