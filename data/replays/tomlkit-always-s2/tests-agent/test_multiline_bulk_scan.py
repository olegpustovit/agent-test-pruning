import pytest

from tomlkit import dumps
from tomlkit import loads
from tomlkit.exceptions import TOMLKitError
from tomlkit.exceptions import UnexpectedEofError


@pytest.mark.parametrize(
    "src, expected",
    [
        ('a = """x\ny\n\tz"""', "x\ny\n\tz"),
        ("a = '''x\ny\n\tz'''", "x\ny\n\tz"),
        ('a = """x\r\ny\r\nz"""', "x\r\ny\r\nz"),
        ("a = '''x\r\ny'''", "x\r\ny"),
        ('a = """\nfirst\nsecond"""', "first\nsecond"),
        ('a = """q"" and "x"""', 'q"" and "x'),
        ("a = '''q'' and 'x'''", "q'' and 'x"),
        ('a = """a\\tb\\\n   c\nd"""', "a\tbc\nd"),
        ("a = '''a\\tb\nd'''", "a\\tb\nd"),
        ('a = """é\n😀\nz"""', "é\n😀\nz"),
        ('a = """x""""', 'x"'),
    ],
)
def test_multiline_values(src, expected):
    doc = loads(src)
    assert doc["a"] == expected
    assert dumps(doc) == src


def test_multiline_followed_by_more_content():
    src = 'a = """l1\nl2"""\nb = \'\'\'m1\nm2\'\'\'\nc = 1\n'
    doc = loads(src)
    assert doc["a"] == "l1\nl2"
    assert doc["b"] == "m1\nm2"
    assert doc["c"] == 1
    assert dumps(doc) == src


@pytest.mark.parametrize("q", ['"""', "'''"])
@pytest.mark.parametrize("bad", ["\r", "\x00", "\x01", "\x1f", "\x7f"])
def test_invalid_chars_rejected(q, bad):
    with pytest.raises(TOMLKitError):
        loads(f"a = {q}ab\ncd{bad}ef{q}")


@pytest.mark.parametrize("q", ['"""', "'''"])
def test_lone_cr_before_lf_ok_but_not_alone(q):
    assert loads(f"a = {q}x\r\ny{q}")["a"] == "x\r\ny"
    with pytest.raises(TOMLKitError):
        loads(f"a = {q}x\ry{q}")


@pytest.mark.parametrize("src", ['a = """abc\ndef', "a = '''abc\ndef", 'a = """abc\\', 'a = """'])
def test_eof_inside_body(src):
    with pytest.raises(UnexpectedEofError):
        loads(src)
