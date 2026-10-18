import pytest

import tomlkit

from tomlkit.exceptions import InvalidControlChar
from tomlkit.exceptions import UnexpectedEofError


@pytest.mark.parametrize(
    "src, expected",
    [
        ('a = """x\ny\tz\nw"""', "x\ny\tz\nw"),
        ('a = """x\r\ny\r\nz"""', "x\r\ny\r\nz"),
        ("a = '''x\ny\tz\n'''", "x\ny\tz\n"),
        ("a = '''x\r\ny'''", "x\r\ny"),
        ('a = """one "two" three"""', 'one "two" three'),
        ('a = """x""\\"y"""', 'x"""y'),
        ('a = """a\\tb\\\n   c"""', "a\tbc"),
        ("a = '''a\\nb'''", "a\\nb"),
        ('a = """héllo \U0001f600\nz"""', "héllo \U0001f600\nz"),
        ('a = """"quoted\\""""', '"quoted"'),
    ],
)
def test_multiline_values(src, expected):
    doc = tomlkit.parse(src)
    assert doc["a"] == expected
    assert doc.as_string() == src


def test_multiline_followed_by_more_content():
    src = 'a = """l1\nl2"""\nb = \'\'\'x\r\ny\'\'\'\nc = 1\n'
    doc = tomlkit.parse(src)
    assert doc["a"] == "l1\nl2"
    assert doc["b"] == "x\r\ny"
    assert doc["c"] == 1
    assert doc.as_string() == src


@pytest.mark.parametrize("q", ['"""', "'''"])
def test_lone_cr_rejected(q):
    with pytest.raises(InvalidControlChar):
        tomlkit.parse(f"a = {q}x\ry{q}")


@pytest.mark.parametrize("q", ['"""', "'''"])
@pytest.mark.parametrize("ch", ["\x00", "\x01", "\x1f", "\x7f"])
def test_control_chars_rejected(q, ch):
    with pytest.raises(InvalidControlChar) as e:
        tomlkit.parse(f"a = {q}ab\ncd{ch}{q}")
    assert e.value.line == 2


@pytest.mark.parametrize("q", ['"""', "'''"])
def test_eof_in_body(q):
    with pytest.raises(UnexpectedEofError):
        tomlkit.parse(f"a = {q}x\ny")
