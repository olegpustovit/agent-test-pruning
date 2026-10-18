import pytest

from tomlkit import dumps
from tomlkit import parse
from tomlkit.exceptions import UnexpectedCharError
from tomlkit.parser import Parser


@pytest.mark.parametrize(
    "src",
    ["a = []\n", "a = [1]\n", "a = [1,]\n", "a = [ 1 , ]\n", "a = [[], [1,], [ ]]\n"],
)
def test_valid_arrays_build_no_error(src, monkeypatch):
    calls = []
    orig = Parser.parse_error

    def spy(self, *args, **kwargs):
        calls.append(args)
        return orig(self, *args, **kwargs)

    monkeypatch.setattr(Parser, "parse_error", spy)
    doc = parse(src)
    assert dumps(doc) == src
    assert calls == []


@pytest.mark.parametrize("src", ["a = [,]\n", "a = [1,,]\n", "a = [1 2]\n"])
def test_malformed_arrays_still_raise(src):
    with pytest.raises(UnexpectedCharError):
        parse(src)
