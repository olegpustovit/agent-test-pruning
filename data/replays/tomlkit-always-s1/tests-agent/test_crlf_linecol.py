import pytest

from tomlkit import parse
from tomlkit.exceptions import UnexpectedCharError


@pytest.mark.parametrize(
    "doc, line, col",
    [
        ("a = 1\r\nb = 2\r\nc = = 3\r\n", 3, 4),
        ("a = 1\nb = 2\nc = = 3\n", 3, 4),
        ("a = 1\r\nb = 2\r\nc = 3\r\nd = = 4\r\n", 4, 4),
        ("a = 1\nb = 2\r\nc = 3\nd = = 4\r\n", 4, 4),
        ("a = = 1\r\n", 1, 4),
    ],
)
def test_error_position_line_endings(doc, line, col):
    with pytest.raises(UnexpectedCharError) as exc:
        parse(doc)
    assert (exc.value.line, exc.value.col) == (line, col)
