import pytest

from tomlkit import loads
from tomlkit.exceptions import ParseError


@pytest.mark.parametrize("doc", ["a\tb = 1", "a\tb\t= 1", "[a\tb]\nx = 1"])
def test_tab_inside_bare_key_rejected(doc):
    with pytest.raises(ParseError):
        loads(doc)


def test_tab_around_key_still_allowed():
    assert loads("a\t= 1")["a"] == 1
    assert loads("\ta = 1")["a"] == 1


def test_space_inside_bare_key_still_rejected():
    with pytest.raises(ParseError):
        loads("a b = 1")
