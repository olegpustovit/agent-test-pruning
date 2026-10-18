import os

import pytest

from boltons import fileutils
from boltons.fileutils import AtomicSaver, atomic_save


def _spy_fsync(monkeypatch):
    calls = []
    real = os.fsync

    def spy(fd):
        calls.append(fd)
        return real(fd)

    monkeypatch.setattr(fileutils.os, 'fsync', spy)
    return calls


def test_fsync_called_on_success(tmp_path, monkeypatch):
    calls = _spy_fsync(monkeypatch)
    dest = tmp_path / 'out.txt'
    with atomic_save(str(dest)) as f:
        f.write(b'hello')
    assert len(calls) == 1
    assert dest.read_bytes() == b'hello'


def test_fsync_uses_part_file_fd_after_flush(tmp_path, monkeypatch):
    # data must be flushed to the OS before fsync, so file size is visible
    sizes = []
    real = os.fsync

    def spy(fd):
        sizes.append(os.fstat(fd).st_size)
        return real(fd)

    monkeypatch.setattr(fileutils.os, 'fsync', spy)
    with atomic_save(str(tmp_path / 'o.bin'), buffering=8192) as f:
        f.write(b'x' * 100)
    assert sizes == [100]


def test_fsync_before_close_and_rename(tmp_path, monkeypatch):
    order = []
    real_fsync = os.fsync
    real_rename = fileutils.atomic_rename
    dest = tmp_path / 'o.txt'

    def spy_fsync(fd):
        order.append('fsync')
        return real_fsync(fd)

    def spy_rename(*a, **kw):
        order.append('rename')
        return real_rename(*a, **kw)

    monkeypatch.setattr(fileutils.os, 'fsync', spy_fsync)
    monkeypatch.setattr(fileutils, 'atomic_rename', spy_rename)
    saver = AtomicSaver(str(dest))
    with saver as f:
        f.write(b'data')
    assert order == ['fsync', 'rename']
    assert saver.part_file.closed


def test_fsync_called_on_exception_and_error_propagates(tmp_path, monkeypatch):
    calls = _spy_fsync(monkeypatch)
    dest = tmp_path / 'o.txt'
    with pytest.raises(RuntimeError):
        with atomic_save(str(dest)) as f:
            f.write(b'partial')
            raise RuntimeError('boom')
    assert len(calls) == 1
    assert not dest.exists()
    assert not os.path.exists(str(dest) + '.part')


def test_text_mode_fsync(tmp_path, monkeypatch):
    calls = _spy_fsync(monkeypatch)
    dest = tmp_path / 'o.txt'
    with atomic_save(str(dest), text_mode=True) as f:
        f.write('héllo')
    assert len(calls) == 1
    assert dest.read_text(encoding='utf-8') == 'héllo'


def test_fsync_error_propagates(tmp_path, monkeypatch):
    def bad(fd):
        raise OSError(5, 'io error')

    monkeypatch.setattr(fileutils.os, 'fsync', bad)
    dest = tmp_path / 'o.txt'
    with pytest.raises(OSError):
        with atomic_save(str(dest)) as f:
            f.write(b'x')
    assert not dest.exists()


def test_no_fsync_if_setup_fails(tmp_path, monkeypatch):
    calls = _spy_fsync(monkeypatch)
    dest = tmp_path / 'o.txt'
    dest.write_bytes(b'orig')
    with pytest.raises(OSError):
        with atomic_save(str(dest), overwrite=False):
            pass
    assert calls == []
    assert dest.read_bytes() == b'orig'
