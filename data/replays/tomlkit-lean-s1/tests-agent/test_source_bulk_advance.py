import tomlkit

from tomlkit.source import Source


def test_advance_while_stops_on_first_non_member():
    s = Source("  \tabc")
    assert s.advance_while(frozenset(" \t")) is True
    assert s.idx == 3
    assert s.current == "a"


def test_advance_while_no_match_does_not_move():
    s = Source("abc")
    assert s.advance_while(frozenset(" ")) is True
    assert s.idx == 0 and s.current == "a"


def test_advance_while_reaches_eof():
    s = Source("   ")
    assert s.advance_while(frozenset(" ")) is False
    assert s.end() and s.idx == 3


def test_advance_while_from_midpoint_and_empty():
    s = Source("ab  c")
    s.inc()
    s.inc()
    assert s.advance_while(frozenset(" "))
    assert s.idx == 4 and s.current == "c"
    e = Source("")
    assert e.advance_while(frozenset(" ")) is False
    assert e.end()


def test_advance_until_stops_on_first_member():
    s = Source("123 456")
    assert s.advance_until(frozenset(" ")) is True
    assert s.idx == 3 and s.current == " "


def test_advance_until_immediate_and_eof():
    s = Source(" x")
    assert s.advance_until(frozenset(" ")) is True
    assert s.idx == 0
    t = Source("123")
    assert t.advance_until(frozenset(" ")) is False
    assert t.end() and t.idx == 3
    assert t.advance_until(frozenset(" ")) is False


def test_parse_runs_roundtrip():
    doc = (
        "  a  .  b-c_1 =  12_345   # c\n"
        "d = 1979-05-27 07:32:00Z\t# t\n"
        "e = [1, 2.5e3,-inf]\n"
        "f = {x = 1,y=0xff}\n"
        "g = 1979-05-27 \n"
        "h = 1\t"
    )
    parsed = tomlkit.parse(doc)
    assert parsed.as_string() == doc
    assert parsed["a"]["b-c_1"] == 12345
    assert parsed["f"]["y"] == 255
    assert parsed["e"][2] == float("-inf")
