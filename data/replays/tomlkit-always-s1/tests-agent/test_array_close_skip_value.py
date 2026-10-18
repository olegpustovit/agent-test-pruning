import pytest

from tomlkit import dumps
from tomlkit import loads
from tomlkit.exceptions import UnexpectedCharError
from tomlkit.parser import Parser


@pytest.mark.parametrize(
    "src",
    [
        "a = []\n",
        "a = [ ]\n",
        "a = [1]\n",
        "a = [1,]\n",
        "a = [1, 2, ]\n",
        "a = [\n  1,\n  2,\n]\n",
        "a = [ # c\n]\n",
        "a = [[], [1,], [[]]]\n",
        "a = [{b = []}, {c = [1,]}]\n",
    ],
)
def test_array_roundtrip(src):
    assert dumps(loads(src)) == src


def test_values_parsed():
    doc = loads("a = [1, 2,]\nb = []\nc = [[1,], []]\n")
    assert doc["a"] == [1, 2]
    assert doc["b"] == []
    assert doc["c"] == [[1], []]


def test_no_value_attempt_on_closing_bracket():
    for src, calls in [("[]", 0), ("[1,]", 1), ("[1, 2 ,]", 2)]:
        parser = Parser(src)
        count = 0
        orig = parser._parse_value

        def counting():
            nonlocal count
            count += 1
            return orig()

        parser._parse_value = counting
        parser._parse_array()
        assert count == calls


def test_no_unexpected_char_error_built_for_valid_arrays(monkeypatch):
    built = []
    orig = Parser.parse_error

    def spy(self, kind, *a, **kw):
        built.append(kind)
        return orig(self, kind, *a, **kw)

    monkeypatch.setattr(Parser, "parse_error", spy)
    loads("a = []\nb = [1, 2,]\nc = [\n 1,\n]\n")
    assert UnexpectedCharError not in built


@pytest.mark.parametrize(
    "src,line,col",
    [
        ("a = [,]\n", 1, 5),
        ("a = [1,,]\n", 1, 7),
        ("a = [1 2]\n", 1, 7),
        ("x = 1\na = [\n  ,\n]\n", 3, 2),
    ],
)
def test_malformed_arrays_still_error(src, line, col):
    with pytest.raises(UnexpectedCharError) as e:
        loads(src)
    assert (e.value.line, e.value.col) == (line, col)


def test_unterminated_array_errors():
    with pytest.raises(Exception):
        loads("a = [1,")
    with pytest.raises(Exception):
        loads("a = [")
