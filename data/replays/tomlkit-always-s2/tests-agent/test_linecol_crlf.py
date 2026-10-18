import pytest

import tomlkit

from tomlkit.exceptions import ParseError
from tomlkit.source import Source


def _err(doc):
    with pytest.raises(ParseError) as e:
        tomlkit.parse(doc)
    return e.value.line, e.value.col


@pytest.mark.parametrize("nl", ["\n", "\r\n"])
def test_error_position_independent_of_line_ending(nl):
    doc = nl.join(["a = 1", "b = 2", "c = 3", "d = ", ""])
    assert _err(doc) == (4, 4)


def test_crlf_many_lines_before_error():
    doc = "\r\n".join(["k%d = %d" % (i, i) for i in range(20)] + ["x = "]) + "\r\n"
    assert _err(doc) == (21, 4)


@pytest.mark.parametrize(
    "text, idx, expected",
    [
        ("ab\r\ncd\r\nef", 0, (1, 0)),
        ("ab\r\ncd\r\nef", 4, (2, 0)),
        ("ab\r\ncd\r\nef", 5, (2, 1)),
        ("ab\r\ncd\r\nef", 8, (3, 0)),
        ("ab\ncd\r\nef\n", 7, (3, 0)),
        ("ab\ncd\r\nef\n", 8, (3, 1)),
    ],
)
def test_to_linecol_mixed(text, idx, expected):
    s = Source(text)
    s._idx = idx
    assert s._to_linecol() == expected


def test_to_linecol_past_end():
    s = Source("ab\r\ncd\r\n")
    s._idx = 100
    assert s._to_linecol() == (2, 0)
