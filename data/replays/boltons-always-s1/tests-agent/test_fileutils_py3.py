import os

import pytest

from boltons import fileutils
from boltons.fileutils import AtomicSaver, DummyFile, iter_find_files, copy_tree


def test_atomic_saver_exit_with_exception_no_part_file(tmp_path):
    saver = AtomicSaver(str(tmp_path / 'out.txt'))
    saver.__exit__(ValueError, ValueError('x'), None)


def test_atomic_saver_roundtrip(tmp_path):
    dest = tmp_path / 'out.txt'
    with AtomicSaver(str(dest)) as f:
        f.write(b'hi')
    assert dest.read_bytes() == b'hi'


def test_iter_find_files_str_patterns(tmp_path):
    (tmp_path / 'a.py').write_text('')
    (tmp_path / 'b.txt').write_text('')
    found = sorted(os.path.basename(p) for p in iter_find_files(str(tmp_path), '*.py'))
    assert found == ['a.py']
    found = sorted(os.path.basename(p)
                   for p in iter_find_files(str(tmp_path), ['*.py', '*.txt'], ignored='*.txt'))
    assert found == ['a.py']


def test_copy_tree_error_in_copystat_is_reported(tmp_path, monkeypatch):
    src = tmp_path / 'src'
    src.mkdir()
    (src / 'f').write_text('x')

    def bad(*a, **k):
        raise OSError('boom')
    monkeypatch.setattr(fileutils, 'copystat', bad)
    with pytest.raises(fileutils.Error) as ei:
        copy_tree(str(src), str(tmp_path / 'dst'))
    assert any('boom' in e[2] for e in ei.value.args[0])


def test_dummyfile_plain_class_and_behaviour():
    assert DummyFile.__bases__ == (object,)
    d = DummyFile('/x')
    assert d.read() == '' and d.readlines() == []
    d.write('abc')
    with d:
        pass
    d.close()
    with pytest.raises(ValueError):
        d.read()
    assert not hasattr(fileutils, 'file')
