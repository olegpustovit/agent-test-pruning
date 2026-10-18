import pytest

from tomlkit.exceptions import ParseError
from tomlkit.parser import Parser


@pytest.mark.parametrize("doc", ["a\tb = 1", "a\tb\t= 1", "[a\tb]\nx = 1"])
def test_tab_in_bare_key_rejected(doc):
    with pytest.raises(ParseError):
        Parser(doc).parse()


def test_tab_around_key_allowed():
    assert Parser("a\t=\t1").parse()["a"] == 1
