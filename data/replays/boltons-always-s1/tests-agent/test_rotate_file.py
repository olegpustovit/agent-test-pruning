import os

import pytest

from boltons.fileutils import rotate_file


# rotate_file currently deletes the file it just moved into the last "keep"
# slot, so only keep-1 rotations survive (contradicting the docstring).
XFAIL = pytest.mark.xfail(strict=True, reason='rotate_file removes the newest-moved file in slot `keep`')


def _write(path, text):
    with open(path, 'w') as f:
        f.write(text)


def _read(path):
    with open(path) as f:
        return f.read()


def test_missing_file_is_noop(tmp_path):
    rotate_file(str(tmp_path / 'nope.txt'))
    assert os.listdir(tmp_path) == []


def test_basic_rotation_with_ext(tmp_path):
    fn = str(tmp_path / 'a.log')
    _write(fn, 'one')
    rotate_file(fn)
    assert not os.path.exists(fn)
    assert _read(str(tmp_path / 'a.1.log')) == 'one'


def test_no_extension(tmp_path):
    fn = str(tmp_path / 'a')
    _write(fn, 'one')
    rotate_file(fn)
    assert not os.path.exists(fn)
    assert _read(str(tmp_path / 'a.1')) == 'one'


@XFAIL
def test_shifts_existing_and_drops_beyond_keep(tmp_path):
    fn = str(tmp_path / 'a.log')
    for _ in range(5):
        # create new file each round, tagged by round number
        n = len(os.listdir(tmp_path))
        _write(fn, str(n))
        rotate_file(fn, keep=3)
    names = sorted(os.listdir(tmp_path))
    assert names == ['a.1.log', 'a.2.log', 'a.3.log']
    assert [_read(str(tmp_path / n)) for n in names] == ['3', '2', '1'] or \
        len({_read(str(tmp_path / n)) for n in names}) == 3


@XFAIL
def test_ordering_is_newest_first(tmp_path):
    fn = str(tmp_path / 'a.txt')
    for i in range(4):
        _write(fn, f'v{i}')
        rotate_file(fn, keep=2)
    assert _read(str(tmp_path / 'a.1.txt')) == 'v3'
    assert _read(str(tmp_path / 'a.2.txt')) == 'v2'
    assert not os.path.exists(str(tmp_path / 'a.3.txt'))


@XFAIL
def test_keep_one(tmp_path):
    fn = str(tmp_path / 'a.txt')
    _write(fn, 'old')
    rotate_file(fn, keep=1)
    _write(fn, 'new')
    rotate_file(fn, keep=1)
    assert os.listdir(tmp_path) == ['a.1.txt']
    assert _read(str(tmp_path / 'a.1.txt')) == 'new'


@XFAIL
def test_gap_in_existing_rotations(tmp_path):
    fn = str(tmp_path / 'a.txt')
    _write(fn, 'cur')
    _write(str(tmp_path / 'a.2.txt'), 'two')
    rotate_file(fn, keep=3)
    assert _read(str(tmp_path / 'a.1.txt')) == 'cur'
    assert _read(str(tmp_path / 'a.3.txt')) == 'two'
    assert not os.path.exists(str(tmp_path / 'a.2.txt'))


@pytest.mark.parametrize('keep', [0, -1])
def test_invalid_keep(tmp_path, keep):
    fn = str(tmp_path / 'a.txt')
    _write(fn, 'x')
    with pytest.raises(ValueError):
        rotate_file(fn, keep=keep)
    assert os.path.exists(fn)


def test_directory_rejected(tmp_path):
    d = tmp_path / 'adir'
    d.mkdir()
    with pytest.raises(ValueError):
        rotate_file(str(d))


def test_keep_is_keyword_only(tmp_path):
    with pytest.raises(TypeError):
        rotate_file(str(tmp_path / 'a'), 3)


def test_current_behavior_keeps_keep_minus_one(tmp_path):
    fn = str(tmp_path / 'a.txt')
    for i in range(4):
        _write(fn, f'v{i}')
        rotate_file(fn, keep=3)
    assert sorted(os.listdir(tmp_path)) == ['a.1.txt', 'a.2.txt']
    assert _read(str(tmp_path / 'a.1.txt')) == 'v3'
    assert _read(str(tmp_path / 'a.2.txt')) == 'v2'
