import io
import pytest
from boltons import ioutils

CLASSES = [(ioutils.SpooledBytesIO, b"abc\ndef\n", b"x"),
           (ioutils.SpooledStringIO, u"abc\ndef\n", u"x")]
ids = ["bytes", "string"]


def mk(cls, data):
    f = cls()
    f.write(data)
    f.seek(0)
    return f


@pytest.fixture(params=CLASSES, ids=ids)
def kit(request):
    return request.param


def test_iobase_inheritance(kit):
    cls, data, _ = kit
    f = cls()
    assert isinstance(f, io.IOBase)
    assert isinstance(f, ioutils.SpooledIOBase)


def test_closed_raises(kit):
    cls, data, _ = kit
    f = mk(cls, data)
    f.close()
    for call in (lambda: f.read(), lambda: f.write(data), lambda: f.seek(0),
                 lambda: f.tell(), lambda: f.readline(), lambda: f.flush(),
                 lambda: f.isatty(), lambda: f.truncate(), lambda: f.getvalue(),
                 lambda: iter(f), lambda: next(f), lambda: f.writelines([data]),
                 lambda: f.__enter__()):
        with pytest.raises(ValueError):
            call()


def test_writelines(kit):
    cls, data, _ = kit
    f = cls()
    f.writelines([data, data])
    assert f.getvalue() == data * 2


def test_next_iteration(kit):
    cls, data, _ = kit
    f = mk(cls, data)
    assert list(f) == data.splitlines(True)
    assert f.next is not None


def test_eq_ne_and_position_preserved(kit):
    cls, data, extra = kit
    a, b, c = mk(cls, data), mk(cls, data), mk(cls, data + extra)
    a.seek(3)
    b.seek(1)
    assert a == b
    assert not (a != b)
    assert a.tell() == 3 and b.tell() == 1
    assert a != c and not (a == c)
    assert c != a
    assert a != object()


def test_eq_error_resets_position(kit):
    cls, data, _ = kit
    a, b = mk(cls, data), mk(cls, data)
    a.seek(2)
    b.seek(3)

    def boom(*args, **kw):
        raise RuntimeError("boom")
    b.readline = boom
    with pytest.raises(RuntimeError):
        a == b
    assert a.tell() == 2
    assert b.tell() == 3


def test_del_closes(kit):
    cls, data, _ = kit
    f = mk(cls, data)
    buf = f.buffer
    f.__del__()
    assert buf.closed
    f.__del__()  # no error when already closed
