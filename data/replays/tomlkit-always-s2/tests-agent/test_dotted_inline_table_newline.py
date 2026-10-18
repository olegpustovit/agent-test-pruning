import pytest

import tomlkit


@pytest.mark.parametrize("src", ["[a]\nb.c = {x = 1}\n", "[a]\nb.c = {x = 1}"])
def test_add_after_dotted_inline_table_keeps_newline(src):
    doc = tomlkit.parse(src)
    doc["a"]["d"] = 1
    out = doc.as_string()
    assert out == "[a]\nb.c = {x = 1}\nd = 1\n"
    assert tomlkit.parse(out) == {"a": {"b": {"c": {"x": 1}}, "d": 1}}


def test_add_after_dotted_plain_value_unchanged():
    doc = tomlkit.parse("[a]\nb.c = 1\n")
    doc["a"]["d"] = 1
    assert doc.as_string() == "[a]\nb.c = 1\nd = 1\n"
