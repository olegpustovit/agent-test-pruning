import os

import pytest

from boltons.fileutils import iter_find_files


@pytest.fixture
def tree(tmp_path):
    # root/a.txt, root/d1/b.txt, root/d1/d2/c.txt, root/d1/d2/d3/d.txt
    d = tmp_path / 'root'
    path = d
    for name, fname in [(None, 'a.txt'), ('d1', 'b.txt'), ('d2', 'c.txt'), ('d3', 'd.txt')]:
        if name:
            path = path / name
        path.mkdir(parents=True, exist_ok=True)
        (path / fname).write_text('x')
    return str(d)


def _names(it):
    return sorted(os.path.basename(p) for p in it)


def test_default_unlimited(tree):
    assert _names(iter_find_files(tree, '*.txt')) == ['a.txt', 'b.txt', 'c.txt', 'd.txt']


def test_none_is_unlimited(tree):
    assert _names(iter_find_files(tree, '*.txt', max_depth=None)) == ['a.txt', 'b.txt', 'c.txt', 'd.txt']


@pytest.mark.parametrize('depth,expected', [
    (0, ['a.txt']),
    (1, ['a.txt', 'b.txt']),
    (2, ['a.txt', 'b.txt', 'c.txt']),
    (3, ['a.txt', 'b.txt', 'c.txt', 'd.txt']),
    (10, ['a.txt', 'b.txt', 'c.txt', 'd.txt']),
])
def test_max_depth(tree, depth, expected):
    assert _names(iter_find_files(tree, '*.txt', max_depth=depth)) == expected


def test_max_depth_with_include_dirs(tree):
    res = _names(iter_find_files(tree, 'd*', include_dirs=True, max_depth=1))
    # d1 is listed from root (depth 0); d2 from d1 (depth 1); d3 is at depth 2
    assert res == ['d1', 'd2']


def test_max_depth_with_ignored(tree):
    res = _names(iter_find_files(tree, '*.txt', ignored='b.txt', max_depth=2))
    assert res == ['a.txt', 'c.txt']
