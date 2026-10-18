import pytest

import tomlkit


class Wrapper:
    """Mapping-like but not a Mapping; delegates as_string."""

    def __init__(self, doc):
        self._doc = doc

    def as_string(self):
        return self._doc.as_string()

    def keys(self):
        return self._doc.keys()

    def __getitem__(self, k):
        return self._doc[k]


def test_dumps_wrapper_uses_as_string_preserving_layout():
    text = "[b]\nx = 1\n\n# c\n[a]\ny = 2\n"
    assert tomlkit.dumps(Wrapper(tomlkit.parse(text))) == text


def test_dumps_plain_dict_still_works():
    assert tomlkit.dumps({"a": 1}) == "a = 1\n"


def test_dumps_non_mapping_without_as_string_raises():
    with pytest.raises(TypeError, match="Expecting Mapping"):
        tomlkit.dumps(object())
    with pytest.raises(TypeError):
        tomlkit.dumps(5)
