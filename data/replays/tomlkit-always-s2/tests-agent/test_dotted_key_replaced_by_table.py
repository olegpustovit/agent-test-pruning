import pytest

from tomlkit import parse
from tomlkit import table


def _tbl(**kw):
    t = table()
    t.update(kw)
    return t


@pytest.mark.parametrize(
    "src",
    [
        "a.b = 1\n",
        "a.b = 1\nc = 2\n",
        "a.b = 1\nc = 2\nd.e = 3\n",
        "a.b = 1\nc = 2\n[t]\nz = 1\n",
    ],
)
def test_dotted_replaced_by_table_roundtrips(src):
    doc = parse(src)
    expected = {k: v for k, v in doc.unwrap().items()}
    doc["a"] = _tbl(x=1)
    expected["a"] = {"x": 1}
    out = doc.as_string()
    assert out.count("[a]") == 1
    assert "a.x" not in out and "a.b" not in out
    assert parse(out).unwrap() == expected


def test_no_duplicated_prefix():
    doc = parse("a.b = 1\n")
    doc["a"] = _tbl(x=1)
    assert doc.as_string() == "[a]\nx = 1\n"


def test_sibling_not_captured():
    doc = parse("a.b = 1\nc = 2\n")
    doc["a"] = _tbl(x=1)
    assert doc.as_string() == "c = 2\n\n[a]\nx = 1\n"
    assert parse(doc.as_string())["c"] == 2


def test_following_dotted_key_not_captured():
    doc = parse("a.b = 1\nd.e = 3\n")
    doc["a"] = _tbl(x=1)
    out = doc.as_string()
    assert parse(out).unwrap() == {"a": {"x": 1}, "d": {"e": 3}}


def test_plain_value_replaced_by_table_before_dotted_key():
    doc = parse("c = 1\nd.e = 3\n")
    doc["c"] = _tbl(q=1)
    out = doc.as_string()
    assert parse(out).unwrap() == {"c": {"q": 1}, "d": {"e": 3}}


def test_dotted_key_replaced_by_non_table_unchanged():
    doc = parse("a.b = 1\nc = 2\n")
    doc["a"] = 5
    assert parse(doc.as_string()).unwrap() == {"a": 5, "c": 2}
