import pytest

import tomlkit


@pytest.mark.parametrize(
    "src",
    [
        "t = {\n    a = 1,\n    b = 2 # c\n}\n",
        "t = {\n    a = 1, # x\n    b = 2 # c\n}\n",
    ],
)
def test_append_after_trailing_comment_keeps_comma_before_comment(src):
    doc = tomlkit.parse(src)
    doc["t"]["c"] = 3
    out = doc.as_string()

    assert "# c," not in out
    assert "b = 2, # c" in out
    assert tomlkit.parse(out)["t"] == {"a": 1, "b": 2, "c": 3}
    assert tomlkit.parse(out).as_string() == out
