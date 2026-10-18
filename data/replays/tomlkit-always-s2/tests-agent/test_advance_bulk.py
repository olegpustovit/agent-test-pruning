import pytest

from tomlkit import dumps
from tomlkit import parse
from tomlkit.source import Source


SP = frozenset(" \t")


def test_advance_while_stops_on_non_member():
    s = Source("  \tabc")
    assert s.advance_while(SP) is True
    assert s.idx == 3
    assert s.current == "a"


def test_advance_while_no_move():
    s = Source("abc")
    assert s.advance_while(SP) is True
    assert s.idx == 0
    assert s.current == "a"


def test_advance_while_to_eof():
    s = Source("   ")
    assert s.advance_while(SP) is False
    assert s.idx == 3
    assert s.current == Source.EOF


def test_advance_while_from_middle_and_empty():
    s = Source("a  b")
    s.inc()
    assert s.advance_while(SP) is True
    assert s.idx == 3 and s.current == "b"
    e = Source("")
    assert e.advance_while(SP) is False
    assert e.current == Source.EOF


def test_advance_until_stops_on_member():
    s = Source("123, 4")
    assert s.advance_until(frozenset(",]")) is True
    assert s.idx == 3
    assert s.current == ","


def test_advance_until_immediate_and_eof():
    s = Source(",x")
    assert s.advance_until(frozenset(",")) is True
    assert s.idx == 0
    t = Source("abc")
    assert t.advance_until(frozenset(",")) is False
    assert t.idx == 3
    assert t.current == Source.EOF


def test_advance_then_inc_at_eof():
    s = Source("ab")
    s.advance_until(frozenset("z"))
    assert s.inc() is False


@pytest.mark.parametrize(
    "doc",
    [
        "  a = 1\n",
        "a . b = 2\n",
        "[ t ]\n  x\t=\t1.5e3 # c\n",
        "d = 1979-05-27 07:32:00Z\n",
        "d = 1979-05-27 07:32:00 # c\n",
        "d = 1979-05-27\n",
        "a = [1, 2,3 ,4]\nb = {x = 1,y=2}\n",
        "n = -inf\nm = +nan\nh = 0xDEAD_beef\n",
        "k = 1",
        "  \t",
        "x = 1_000   \r\n",
    ],
)
def test_roundtrip(doc):
    assert dumps(parse(doc)) == doc


def test_values():
    doc = parse("a = [1, 2.5, 1979-05-27T07:32:00Z]\nb = {x = 3}\n")
    assert doc["a"][0] == 1 and doc["a"][1] == 2.5
    assert doc["b"]["x"] == 3


def test_bare_key_with_space_rejected():
    from tomlkit.exceptions import ParseError

    with pytest.raises(ParseError):
        parse("a b = 1\n")
