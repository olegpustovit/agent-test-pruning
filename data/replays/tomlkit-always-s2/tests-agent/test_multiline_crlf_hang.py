import pytest

import tomlkit

from tomlkit.exceptions import UnexpectedEofError


@pytest.mark.parametrize("quote", ['"""', "'''"])
def test_multiline_string_with_crlf(quote):
    doc = tomlkit.parse(f"a = {quote}x\r\ny{quote}\r\n")
    assert doc["a"] == "x\r\ny" or doc["a"] == "x\ny"
    assert tomlkit.dumps(doc) == f"a = {quote}x\r\ny{quote}\r\n"


def test_multiline_string_crlf_at_end_of_input_does_not_hang():
    with pytest.raises(UnexpectedEofError):
        tomlkit.parse('a = """x\r\n')


def test_multiline_string_crlf_only_after_open():
    doc = tomlkit.parse('a = """\r\nfoo\r\nbar"""')
    assert doc["a"].replace("\r\n", "\n") == "foo\nbar"
