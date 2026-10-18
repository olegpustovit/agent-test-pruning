import pytest

import tomlkit

from tomlkit.exceptions import ParseError


@pytest.mark.parametrize("doc", ["a\tb = 1", "a\tb\tc = 1", "[a\tb]\nx = 1"])
def test_tab_inside_bare_key_rejected(doc):
    with pytest.raises(ParseError):
        tomlkit.parse(doc)


def test_space_inside_bare_key_still_rejected():
    with pytest.raises(ParseError):
        tomlkit.parse("a b = 1")


def test_tab_around_key_is_whitespace():
    assert tomlkit.parse("a\t= 1") == {"a": 1}
    assert tomlkit.parse("\ta = 1") == {"a": 1}
    assert tomlkit.parse("a\t.\tb = 1") == {"a": {"b": 1}}


def test_tab_in_quoted_key_allowed():
    assert tomlkit.parse('"a\tb" = 1') == {"a\tb": 1}
