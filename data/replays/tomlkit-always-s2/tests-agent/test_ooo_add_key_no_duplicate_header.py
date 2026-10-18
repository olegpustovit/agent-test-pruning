import pytest

from tomlkit import dumps
from tomlkit import parse


@pytest.mark.parametrize(
    "text",
    [
        "[a.b]\nx=1\n\n[a]\n",
        "[a.b]\nx=1\n\n[c]\nq=1\n\n[a]\n",
    ],
)
def test_add_key_to_out_of_order_table_no_duplicate_header(text):
    doc = parse(text)
    doc["a"]["z"] = 3
    out = dumps(doc)
    assert out.count("[a]") == 1
    reparsed = parse(out)
    assert reparsed["a"]["z"] == 3
    assert reparsed["a"]["b"]["x"] == 1
    assert reparsed.unwrap()["a"] == {"b": {"x": 1}, "z": 3}


def test_added_key_lands_under_concrete_header():
    doc = parse("[a.b]\nx=1\n\n[a]\n")
    doc["a"]["z"] = 3
    assert dumps(doc) == "[a.b]\nx=1\n\n[a]\nz = 3\n"
