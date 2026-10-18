import pytest

from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


def test_super_table_extended_by_dotted_key_out_of_order():
    doc = "[a.b.c]\n[a]\nb.z = 1\n"
    parsed = parse(doc)
    assert parsed.unwrap() == {"a": {"b": {"c": {}, "z": 1}}}
    assert parsed.as_string() == doc


@pytest.mark.parametrize(
    "doc",
    [
        "[a.b]\n[a]\nb.z = 1\n",
        "[a.b.c]\n[a]\nb.c.z = 1\n",
        "[a.b.c]\n[a]\nb.z = 1\nb.z = 2\n",
    ],
)
def test_dotted_key_conflicting_with_existing_table_rejected(doc):
    with pytest.raises(TOMLKitError):
        parse(doc)
