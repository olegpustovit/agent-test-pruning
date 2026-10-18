import pytest

import tomlkit

from tomlkit.exceptions import InvalidCharInStringError
from tomlkit.exceptions import InvalidDateError
from tomlkit.exceptions import InvalidDateTimeError
from tomlkit.exceptions import InvalidTimeError
from tomlkit.exceptions import UnexpectedCharError
from tomlkit.items import Whitespace


def test_array_default_and_none_like():
    a = tomlkit.array()
    assert a == []
    assert a.as_string() == "[]"
    assert tomlkit.array("[1, 2]") == [1, 2]
    # default is not shared between calls
    assert tomlkit.array() is not tomlkit.array()


def test_unexpected_char_message_uses_repr():
    assert "Unexpected character: 'a'" in str(UnexpectedCharError(1, 2, "a"))
    assert "Invalid character '\\n' in string" in str(
        InvalidCharInStringError(1, 2, "\n")
    )


def test_whitespace_repr():
    assert repr(Whitespace("  \n")) == "<Whitespace '  \\n'>"


@pytest.mark.parametrize(
    "doc, exc",
    [
        ("a = 2020-13-01", InvalidDateError),
        ("a = 10:61:00", InvalidTimeError),
        ("a = 2020-01-01T25:00:00", InvalidDateTimeError),
    ],
)
def test_invalid_dates_suppress_context(doc, exc):
    with pytest.raises(exc) as e:
        tomlkit.parse(doc)
    assert e.value.__suppress_context__
    assert e.value.__cause__ is None


def test_unterminated_string_error():
    with pytest.raises(tomlkit.exceptions.UnexpectedEofError) as e:
        tomlkit.parse('a = "abc')
    assert e.value.__cause__ is None


def test_container_multi_index_tuples():
    doc = tomlkit.parse("[[a]]\nx = 1\n[[a]]\nx = 2\n[[a]]\nx = 3\n")
    assert [t["x"] for t in doc["a"]] == [1, 2, 3]
    assert tomlkit.dumps(doc) == "[[a]]\nx = 1\n[[a]]\nx = 2\n[[a]]\nx = 3\n"

    doc = tomlkit.parse("[a.b]\nx = 1\n[c]\ny = 2\n[a.d]\nz = 3\n")
    doc["a"]["e"] = 4
    assert tomlkit.parse(tomlkit.dumps(doc))["a"]["e"] == 4
    assert doc["a"]["d"]["z"] == 3
