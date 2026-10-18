import pytest

from tomlkit import loads
from tomlkit.exceptions import InvalidControlChar
from tomlkit.exceptions import UnexpectedEofError


@pytest.mark.parametrize(
    "src, expected",
    [
        ('a = """one\ntwo\n\tthree"""', "one\ntwo\n\tthree"),
        ("a = '''one\ntwo\n\tthree'''", "one\ntwo\n\tthree"),
        ('a = """x\r\ny\r\nz"""', "x\r\ny\r\nz"),
        ("a = '''x\r\ny\r\nz'''", "x\r\ny\r\nz"),
        ('a = """q"" and "\nend"""', 'q"" and "\nend'),
        ("a = '''q'' and '\nend'''", "q'' and '\nend"),
        ('a = """a\\tb\\\n   c\nd"""', "a\tbc\nd"),
        ("a = '''a\\tb\nc'''", "a\\tb\nc"),
        ('a = """é\n日本\n😀"""', "é\n日本\n😀"),
        ('a = """\n' + "line\n" * 5000 + '"""', "line\n" * 5000),
    ],
)
def test_multiline_values_roundtrip(src, expected):
    doc = loads(src)
    assert doc["a"] == expected
    assert doc.as_string() == src


@pytest.mark.parametrize("ch", ["\x00", "\x01", "\x1f", "\x7f"])
def test_multiline_control_char_rejected(ch):
    with pytest.raises(InvalidControlChar):
        loads(f'a = """ab\ncd{ch}ef"""')
    with pytest.raises(InvalidControlChar):
        loads(f"a = '''ab\ncd{ch}ef'''")


def test_multiline_lone_cr_rejected():
    with pytest.raises(InvalidControlChar):
        loads('a = """ab\ncd\ref"""')
    with pytest.raises(InvalidControlChar):
        loads("a = '''ab\ncd\ref'''")


@pytest.mark.parametrize(
    "src", ['a = """abc\ndef', "a = '''abc\ndef", 'a = """abc\ndef\\']
)
def test_multiline_unterminated_eof(src):
    with pytest.raises(UnexpectedEofError):
        loads(src)
