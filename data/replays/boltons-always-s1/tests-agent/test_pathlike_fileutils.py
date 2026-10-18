import os
import pathlib

from boltons.fileutils import AtomicSaver, iter_find_files


def test_atomic_saver_pathlike(tmp_path):
    dest = tmp_path / 'out.txt'
    with AtomicSaver(dest) as f:
        f.write(b'hi')
    assert dest.read_bytes() == b'hi'
    assert not (tmp_path / 'out.txt.part').exists()


def test_atomic_saver_pathlike_attrs(tmp_path):
    saver = AtomicSaver(tmp_path / 'x.bin')
    assert isinstance(saver.dest_path, str)
    assert saver.part_path == os.path.join(str(tmp_path), 'x.bin.part')


def test_atomic_saver_pathlike_relative(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    saver = AtomicSaver(pathlib.Path('rel.txt'))
    assert saver.part_path == str(tmp_path / 'rel.txt') + '.part'


def test_iter_find_files_pathlike(tmp_path):
    (tmp_path / 'a.py').write_text('')
    (tmp_path / 'sub').mkdir()
    (tmp_path / 'sub' / 'b.py').write_text('')
    found = sorted(iter_find_files(tmp_path, '*.py'))
    assert found == sorted([str(tmp_path / 'a.py'), str(tmp_path / 'sub' / 'b.py')])
    assert sorted(iter_find_files(tmp_path, '*.py', max_depth=0)) == [str(tmp_path / 'a.py')]
