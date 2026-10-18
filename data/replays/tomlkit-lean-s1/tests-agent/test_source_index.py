import pytest

from tomlkit.exceptions import UnexpectedEofError
from tomlkit.source import Source


def test_initial_position():
    s = Source("abc")
    assert s.idx == 0
    assert s.current == "a"
    assert not s.end()


def test_empty_source_is_eof():
    s = Source("")
    assert s.end()
    assert s.idx == 0
    assert not s.inc()


def test_inc_to_end_and_stay_there():
    s = Source("ab")
    assert s.inc()
    assert s.current == "b"
    assert not s.inc()
    assert s.end() and s.idx == 2
    assert not s.inc()
    assert s.idx == 2 and s.end()


def test_inc_exception_at_end():
    s = Source("a")
    with pytest.raises(UnexpectedEofError):
        s.inc(exception=UnexpectedEofError)


def test_inc_n():
    s = Source("abcd")
    assert s.inc_n(2)
    assert s.current == "c"
    assert not s.inc_n(5)
    assert s.end()


def test_state_restores_on_exception_and_explicit_restore():
    s = Source("abcdef")
    with s.state(restore=True):
        s.inc_n(3)
        assert s.current == "d"
    assert (s.idx, s.current) == (0, "a")

    with pytest.raises(ValueError):
        with s.state:
            s.inc_n(2)
            raise ValueError
    assert (s.idx, s.current) == (0, "a")

    with s.state:
        s.inc_n(2)
    assert (s.idx, s.current) == (2, "c")


def test_restore_after_reaching_eof():
    s = Source("ab")
    with s.state(restore=True):
        s.inc_n(5)
        assert s.end()
    assert s.current == "a" and not s.end()
    assert s.inc() and s.current == "b"


def test_marker_and_extract():
    s = Source("hello world")
    s.inc_n(2)
    s.mark()
    s.inc_n(3)
    assert s.extract() == "llo"
    with s.state(save_marker=True, restore=True):
        s.inc()
        s.mark()
    assert s.marker == 2


def test_multibyte_chars():
    s = Source("é€x")
    assert s.current == "é"
    s.inc()
    assert s.current == "€"
    s.inc()
    assert s.current == "x"
