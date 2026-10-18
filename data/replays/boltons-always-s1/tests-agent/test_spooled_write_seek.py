import pytest
from boltons import ioutils


@pytest.mark.parametrize('conv', [bytes, bytearray, memoryview])
def test_bytes_write_accepts_bytes_like_and_returns_count(conv):
    f = ioutils.SpooledBytesIO()
    assert f.write(conv(b'abc')) == 3
    assert f.getvalue() == b'abc'


def test_bytes_write_rollover_with_memoryview():
    f = ioutils.SpooledBytesIO(max_size=4)
    assert f.write(memoryview(b'abcdef')) == 6
    assert f._rolled
    assert f.getvalue() == b'abcdef'


def test_bytes_write_text_raises():
    with pytest.raises(TypeError):
        ioutils.SpooledBytesIO().write('x')


def test_string_write_returns_len():
    f = ioutils.SpooledStringIO()
    assert f.write('—ab') == 3


@pytest.mark.parametrize('max_size', [1000, 2])
def test_string_backwards_seek_cur(max_size):
    f = ioutils.SpooledStringIO(max_size=max_size)
    f.write('—a—b—c')
    f.seek(0)
    assert f.read(4) == '—a—b'
    assert f.seek(-2, 1) == 2
    assert f.read() == '—b—c'
    f.seek(3)
    f.seek(-1, 1)
    assert f.tell() == 2
    assert f.read(1) == '—'


def test_string_negative_seeks_raise():
    f = ioutils.SpooledStringIO()
    f.write('abc')
    with pytest.raises(ValueError):
        f.seek(-1)
    f.seek(1)
    with pytest.raises(ValueError):
        f.seek(-2, 1)
