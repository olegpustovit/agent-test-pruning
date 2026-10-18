import pytest

from tomlkit.exceptions import UnexpectedEofError
from tomlkit.source import Source


def test_initial_state():
    s = Source("abc")
    assert s.idx == 0
    assert s.current == "a"
    assert not s.end()


def test_empty_source_is_eof():
    s = Source("")
    assert s.end()
    assert s.idx == 0
    assert s.current == Source.EOF


def test_inc_walks_and_pins_at_end():
    s = Source("ab")
    assert s.inc()
    assert (s.idx, s.current) == (1, "b")
    assert not s.inc()
    assert s.end() and s.idx == 2
    # further increments stay pinned
    assert not s.inc()
    assert s.idx == 2 and s.end()


def test_inc_raises_at_end():
    s = Source("a")
    with pytest.raises(UnexpectedEofError):
        s.inc(exception=UnexpectedEofError)
    assert s.end()


def test_inc_n():
    s = Source("abcd")
    assert s.inc_n(2)
    assert s.current == "c"
    assert not s.inc_n(5)
    assert s.end()


def test_extract_and_mark():
    s = Source("hello")
    s.inc()
    s.mark()
    s.inc_n(2)
    assert s.extract() == "el"


def test_state_restores_on_exception():
    s = Source("abcd")
    with pytest.raises(ValueError):
        with s.state:
            s.inc_n(2)
            raise ValueError
    assert (s.idx, s.current) == (0, "a")


def test_state_restore_flag_and_nested():
    s = Source("abcd")
    s.inc()
    with s.state(restore=True):
        s.inc_n(2)
        assert s.current == "d"
    assert (s.idx, s.current) == (1, "b")

    with s.state:
        s.inc()
        with s.state(restore=True):
            s.inc()
        assert (s.idx, s.current) == (2, "c")
    # no restore without exception/flag
    assert (s.idx, s.current) == (2, "c")


def test_state_restore_from_eof():
    s = Source("ab")
    with s.state(restore=True):
        s.inc_n(5)
        assert s.end()
    assert (s.idx, s.current) == (0, "a")
    assert not s.end()


def test_state_marker_saved_only_when_requested():
    s = Source("abcd")
    s.inc()
    s.mark()
    with s.state(restore=True):
        s.inc()
        s.mark()
    assert s.marker == 2
    with s.state(save_marker=True, restore=True):
        s.inc()
        s.mark()
    assert s.marker == 2


def test_reset():
    s = Source("abc")
    s.reset()
    assert s.idx == 1
    assert s.marker == 1


def test_unicode_chars():
    s = Source("é😀")
    assert s.current == "é"
    s.inc()
    assert s.current == "😀"
    assert not s.inc()
