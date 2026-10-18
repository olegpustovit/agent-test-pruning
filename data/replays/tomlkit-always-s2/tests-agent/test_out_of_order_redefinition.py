import pytest

from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


@pytest.mark.parametrize(
    "doc",
    [
        "[a]\nb=1\n[c]\n[a.b]\nd=2\n",
        "[a]\nb.c=1\n[c]\n[a.b]\nd=2\n",
        "[a]\nb={}\n[c]\n[a.b]\nd=2\n",
    ],
)
def test_redefinition_rejected_at_parse_time(doc):
    with pytest.raises(TOMLKitError):
        parse(doc)


def test_dotted_prefix_message():
    with pytest.raises(TOMLKitError, match="Redefinition of an existing table"):
        parse("[a]\nb.c=1\n[c]\n[a.b]\nd=2\n")


@pytest.mark.parametrize(
    "doc, expected",
    [
        ("[a]\n[c]\n[a.b]\nd=2\n", {"a": {"b": {"d": 2}}, "c": {}}),
        ("[a.b]\nd=2\n[c]\n[a]\ne=1\n", {"a": {"b": {"d": 2}, "e": 1}, "c": {}}),
    ],
)
def test_valid_out_of_order_still_parses(doc, expected):
    d = parse(doc)
    assert d.unwrap() == expected
    assert d.as_string() == doc
