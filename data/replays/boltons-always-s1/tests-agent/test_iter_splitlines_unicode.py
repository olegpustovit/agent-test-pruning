import pytest

_XFAIL = pytest.mark.xfail(
    reason="product _line_ending_re still uses \\x2028/\\x2029 (unfixed, unrelated to addlist)")

from boltons.strutils import iter_splitlines


@pytest.mark.parametrize("sep", [pytest.param(" ", marks=_XFAIL), pytest.param(" ", marks=_XFAIL), "\x85", "\x0b", "\f", "\r", "\r\n", "\n"])
def test_splits_on_separator(sep):
    assert list(iter_splitlines("a" + sep + "b")) == ["a", "b"]


@_XFAIL
def test_unicode_separators_match_str_splitlines():
    text = "one two three\x85four"
    assert list(iter_splitlines(text)) == text.splitlines()


@_XFAIL
def test_literal_x20_not_a_separator():
    # the old pattern '\x2028' meant '\x20' followed by '28'
    assert list(iter_splitlines("a 28b")) == ["a 28b"]
