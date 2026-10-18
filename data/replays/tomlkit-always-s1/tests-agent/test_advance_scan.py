import tomlkit

from tomlkit.source import Source


def test_advance_while_stops_at_non_member():
    s = Source("  \t x")
    assert s.advance_while(frozenset(" \t")) is True
    assert s.idx == 4
    assert s.current == "x"


def test_advance_while_no_move():
    s = Source("abc")
    assert s.advance_while(frozenset(" ")) is True
    assert s.idx == 0 and s.current == "a"


def test_advance_while_eof():
    s = Source("   ")
    assert s.advance_while(frozenset(" ")) is False
    assert s.idx == 3
    assert s.end()


def test_advance_while_from_middle_and_empty():
    s = Source("ab  c")
    s.inc_n(2)
    assert s.advance_while(frozenset(" ")) is True
    assert s.current == "c"
    e = Source("")
    assert e.advance_while(frozenset(" ")) is False
    assert e.end()


def test_advance_until():
    s = Source("123,4")
    assert s.advance_until(frozenset(",")) is True
    assert s.idx == 3 and s.current == ","


def test_advance_until_eof():
    s = Source("1234")
    assert s.advance_until(frozenset(",")) is False
    assert s.idx == 4 and s.end()


def test_advance_until_immediate_and_empty():
    s = Source(",x")
    assert s.advance_until(frozenset(",")) is True
    assert s.idx == 0
    assert Source("").advance_until(frozenset(",")) is False


def test_state_restore_after_advance():
    s = Source("   ab")
    with s._state(restore=True):
        s.advance_while(frozenset(" "))
        assert s.idx == 3
    assert s.idx == 0 and s.current == " "


def test_roundtrip_parsing():
    doc = (
        "  \t a . b = 1_000 # c\n"
        "key   =   [1, 2.5e3,0x1F ,  inf]\n"
        "d = 1979-05-27 07:32:00Z\n"
        "e = 1979-05-27 # t\n"
        "f = {x=1,y=2020-01-01T00:00:00}\n"
        "[ t . u ]\n  bare-key_1 = 'v'"
    )
    d = tomlkit.parse(doc)
    assert d.as_string() == doc
    assert d["a"]["b"] == 1000
    assert d["key"] == [1, 2500.0, 31, float("inf")]
    assert str(d["d"].isoformat()) == "1979-05-27T07:32:00+00:00"
    assert d["t"]["u"]["bare-key_1"] == "v"


def test_eof_number_and_key():
    assert tomlkit.parse("a=12").as_string() == "a=12"
    assert tomlkit.parse("a=1979-05-27").as_string() == "a=1979-05-27"
