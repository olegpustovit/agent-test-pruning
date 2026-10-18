import pytest

from tomlkit.exceptions import UnexpectedCharError
from tomlkit.parser import Parser


@pytest.mark.parametrize(
    "sep, line",
    [("\r\n", 4), ("\n", 4), ("\r\n", 4)],
)
def test_error_position_after_crlf_lines(sep, line):
    content = sep.join(["a = 1", "b = 2", "c = 3", "d = 1 x"])
    with pytest.raises(UnexpectedCharError) as e:
        Parser(content).parse()
    assert (e.value.line, e.value.col) == (line, 6)


def test_error_position_mixed_line_endings():
    content = "a = 1\r\nb = 2\nc = 3\r\nd = 1 x"
    with pytest.raises(UnexpectedCharError) as e:
        Parser(content).parse()
    assert (e.value.line, e.value.col) == (4, 6)
