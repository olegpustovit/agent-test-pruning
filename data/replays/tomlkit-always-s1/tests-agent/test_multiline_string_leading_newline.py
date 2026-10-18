import pytest

import tomlkit


@pytest.mark.parametrize("literal", [False, True])
@pytest.mark.parametrize(
    "value", ["\nfoo", "\n\nfoo", "\r\nfoo", "\nMy\nString\n", "\n"]
)
def test_leading_newline_roundtrip(value, literal):
    s = tomlkit.string(value, multiline=True, literal=literal)
    assert str(s) == value
    doc = tomlkit.parse(f"k = {s.as_string()}")
    assert doc["k"] == value


def test_rendering_has_extra_leading_newline():
    assert tomlkit.string("\nfoo", multiline=True).as_string() == '"""\n\nfoo"""'
    assert (
        tomlkit.string("\nfoo", multiline=True, literal=True).as_string()
        == "'''\n\nfoo'''"
    )


def test_unaffected_cases():
    assert tomlkit.string("foo", multiline=True).as_string() == '"""foo"""'
    assert tomlkit.string("a\nb", multiline=True).as_string() == '"""a\nb"""'
    assert tomlkit.string("\nfoo").as_string() == '"\\nfoo"'


def test_document_dumps_roundtrip():
    doc = tomlkit.document()
    doc["k"] = tomlkit.string("\nfoo", multiline=True)
    assert tomlkit.parse(tomlkit.dumps(doc))["k"] == "\nfoo"
