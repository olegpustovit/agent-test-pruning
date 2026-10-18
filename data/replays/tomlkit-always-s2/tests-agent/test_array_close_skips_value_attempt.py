import pytest

from tomlkit import dumps
from tomlkit import parse
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
        "a = [[], [1,], [[2,]]]\n",
        "a = [ # c\n]\n",
        "a = [1, # c\n]\n",
        "a = [{x = 1},]\n",
        "[[t]]\na = [1,]\n[[t]]\na = []\n",
    ],
)
def test_roundtrip(src):
    assert dumps(parse(src)) == src


def test_values():
    doc = parse("a = []\nb = [1, 2,]\nc = [[], [3,]]\n")
    assert doc["a"] == []
    assert doc["b"] == [1, 2]
    assert doc["c"] == [[], [3]]


def test_no_value_parse_attempt_on_close_bracket(monkeypatch):
    calls = []
    orig = Parser._parse_value

    def spy(self):
        calls.append(self._current)
        return orig(self)

    monkeypatch.setattr(Parser, "_parse_value", spy)
    parse("a = [1, 2,]\nb = []\n")
    assert "]" not in calls
    assert calls.count("1") == 1 and calls.count("2") == 1


@pytest.mark.parametrize(
    "src",
    ["a = [,]\n", "a = [1,,]\n", "a = [1 2]\n", "a = [,1]\n"],
)
def test_malformed_still_raises(src):
    with pytest.raises(UnexpectedCharError):
        parse(src)


def test_malformed_position():
    with pytest.raises(UnexpectedCharError) as e:
        parse("x = 1\na = [1,,]\n")
    assert (e.value.line, e.value.col) == (2, 7)


def test_eof_in_array():
    from tomlkit.exceptions import ParseError

    for src in ["a = [", "a = [1,", "a = [1"]:
        with pytest.raises(ParseError):
            parse(src)
