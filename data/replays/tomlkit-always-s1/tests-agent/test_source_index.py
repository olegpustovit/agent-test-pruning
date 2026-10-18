import pytest

from tomlkit.exceptions import UnexpectedEofError
from tomlkit.source import Source


def test_init_positions_on_first_char():
    s = Source("abc")
    assert s.idx == 0
    assert s.current == "a"
    assert not s.end()


def test_empty_source_is_eof():
    s = Source("")
    assert s.end()
    assert s.idx == 0
    assert s.current is Source.EOF


def test_inc_walks_and_pins_at_end():
    s = Source("ab")
    assert s.inc()
    assert (s.idx, s.current) == (1, "b")
    assert not s.inc()
    assert s.idx == 2
    assert s.end()
    # repeated inc past the end stays pinned
    assert not s.inc()
    assert s.idx == 2
    assert s.end()


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


def test_state_restore_on_exception_and_explicit():
    s = Source("abcdef")
    with pytest.raises(ValueError):
        with s.state:
            s.inc_n(3)
            raise ValueError
    assert (s.idx, s.current) == (0, "a")

    with s.state(restore=True):
        s.inc_n(2)
        assert s.current == "c"
    assert (s.idx, s.current) == (0, "a")

    with s.state:
        s.inc_n(2)
    assert (s.idx, s.current) == (2, "c")


def test_state_restore_from_eof():
    s = Source("ab")
    with s.state(restore=True):
        s.inc_n(5)
        assert s.end()
    assert s.idx == 0
    assert s.current == "a"
    assert not s.end()


def test_nested_states_and_marker():
    s = Source("abcdef")
    with s.state(save_marker=True, restore=True):
        s.inc()
        s.mark()
        with s.state(restore=True):
            s.inc_n(2)
        assert s.idx == 1
        s.inc()
        assert s.extract() == "b"
    assert s.idx == 0
    assert s.marker == 0


def test_extract_and_consume():
    s = Source("   xy")
    s.mark()
    s.consume(" ")
    assert s.current == "x"
    assert s.extract() == "   "


def test_multibyte_chars():
    s = Source("é😀z")
    assert s.current == "é"
    s.inc()
    assert s.current == "😀"
    s.inc()
    assert s.current == "z"


def test_reset_after_construction():
    s = Source("ab")
    s.reset()
    # reset advances like inc then marks
    assert s.idx == 1
    assert s.marker == 1
