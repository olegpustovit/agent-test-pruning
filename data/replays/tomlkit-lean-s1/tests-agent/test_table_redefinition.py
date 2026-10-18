import pytest

from tomlkit import parse
from tomlkit.exceptions import ParseError


@pytest.mark.parametrize(
    "doc",
    [
        "[a]\nx = 1\n[a]\ny = 2\n",
        "[a]\n[b]\n[a]\n",
        "[a.b]\n[a]\n[a.b]\n",
        "[a.b.c]\n[x]\n[a.b.c]\n",
    ],
)
def test_table_redefined_after_header_rejected(doc):
    with pytest.raises(ParseError):
        parse(doc)


@pytest.mark.parametrize(
    "doc",
    [
        "[a.b]\n[c]\n[a]\n",
        "[a]\n[c]\n[a.b]\n",
        "[a.b]\n[c]\n[a.d]\n",
    ],
)
def test_super_table_then_distinct_definition_allowed(doc):
    assert parse(doc).as_string() == doc
