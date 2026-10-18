import pytest

import tomlkit

from tomlkit.exceptions import TOMLKitError


@pytest.mark.parametrize(
    "doc",
    [
        "[a]\nb=1\n[x]\n[a.b]\nc=2\n",
        "[a]\nb.c=1\n[x]\n[a.b]\nd=2\n",
        "[a]\n[a.b]\nc=1\n[x]\n[a.b]\nd=2\n",
    ],
)
def test_out_of_order_redefinition_rejected_at_parse(doc):
    with pytest.raises(TOMLKitError):
        tomlkit.parse(doc)


@pytest.mark.parametrize(
    "doc, expected",
    [
        ("[a]\n[x]\n[a.b]\nc=2\n", {"a": {"b": {"c": 2}}, "x": {}}),
        ("[a]\nb=1\n[x]\n[a.c]\nd=2\n", {"a": {"b": 1, "c": {"d": 2}}, "x": {}}),
    ],
)
def test_valid_out_of_order_still_parses(doc, expected):
    parsed = tomlkit.parse(doc)
    assert parsed.unwrap() == expected
    assert tomlkit.dumps(parsed) == doc
