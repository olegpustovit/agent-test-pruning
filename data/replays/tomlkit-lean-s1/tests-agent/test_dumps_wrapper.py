from collections.abc import Mapping

import pytest

import tomlkit


class Wrapper:
    """Non-Mapping wrapper delegating as_string (like dotty_dict's Dotty)."""

    def __init__(self, doc):
        self._doc = doc

    def as_string(self):
        return self._doc.as_string()


def test_dumps_wrapper_preserves_layout():
    content = "[b]\nx = 1\n\n[a]\ny = 2  # c\n"
    assert tomlkit.dumps(Wrapper(tomlkit.parse(content))) == content


def test_dumps_non_mapping_without_as_string_raises_type_error():
    assert not isinstance(object(), Mapping)
    with pytest.raises(TypeError):
        tomlkit.dumps(object())  # type: ignore[arg-type]
