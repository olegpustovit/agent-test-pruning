import pytest

import tomlkit


DOC = '[b]\nx = 1\n\n[a]\ny = 2  # c\n'


class Wrapper:
    """Mapping-like but not a Mapping; delegates as_string."""

    def __init__(self, doc):
        self._doc = doc

    def as_string(self):
        return self._doc.as_string()


def test_wrapper_rendered_via_as_string():
    w = Wrapper(tomlkit.parse(DOC))
    assert tomlkit.dumps(w) == DOC


def test_wrapper_sort_keys_ignored_uses_as_string():
    w = Wrapper(tomlkit.parse(DOC))
    assert tomlkit.dumps(w, sort_keys=True) == DOC


def test_plain_mapping_still_encoded():
    assert tomlkit.dumps({"a": {"b": 1}}) == "[a]\nb = 1\n"


def test_non_mapping_without_as_string_raises_type_error():
    with pytest.raises(TypeError, match="Expecting Mapping"):
        tomlkit.dumps(object())  # type: ignore[arg-type]


def test_document_preserves_layout():
    assert tomlkit.dumps(tomlkit.parse(DOC)) == DOC
