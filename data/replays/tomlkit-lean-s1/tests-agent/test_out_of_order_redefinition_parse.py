import pytest

from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


@pytest.mark.parametrize(
    "doc",
    [
        "[a]\nb = true\n[zz]\nq = 9\n[a.b]\nc = 1\n",
        "[a]\nb.c = 1\n[zz]\nq = 9\n[a.b]\nd = 2\n",
    ],
)
def test_out_of_order_redefinition_rejected_at_parse(doc):
    with pytest.raises(TOMLKitError):
        parse(doc)


def test_out_of_order_non_conflicting_super_table_ok():
    doc = "[a]\nb = 1\n[zz]\nq = 9\n[a.c]\nd = 2\n"
    parsed = parse(doc)
    assert parsed.unwrap() == {"a": {"b": 1, "c": {"d": 2}}, "zz": {"q": 9}}
    assert parsed.as_string() == doc
