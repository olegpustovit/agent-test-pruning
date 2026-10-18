import pytest

import tomlkit


DOC = """[a]
[a.b]
[a.b.c]
x.y.z = 1
w = 2
"""


def test_dumps_deeply_nested_table():
    d = tomlkit.parse(DOC)
    assert tomlkit.dumps(d["a"]["b"]["c"]) == "x.y.z = 1\nw = 2\n"


def test_dumps_intermediate_table_keeps_header():
    d = tomlkit.parse(DOC)
    assert tomlkit.dumps(d["a"]["b"]) == "[a.b.c]\nx.y.z = 1\nw = 2\n"


def test_dumps_inline_table():
    d = tomlkit.parse("t = {a = 1, b = {c = 2}}")
    assert tomlkit.dumps(d["t"]) == "{a = 1, b = {c = 2}}"


def test_dumps_plain_mapping_still_works():
    assert tomlkit.dumps({"a": {"b": 1}}) == "[a]\nb = 1\n"


def test_dumps_invalid_type_message():
    with pytest.raises(TypeError):
        tomlkit.dumps(1)  # type: ignore[arg-type]
