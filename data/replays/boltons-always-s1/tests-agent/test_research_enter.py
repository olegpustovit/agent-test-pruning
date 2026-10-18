import pytest

from boltons.iterutils import research, remap, default_enter


class Box:
    def __init__(self, items):
        self.items = items


def box_enter(path, key, value):
    if isinstance(value, Box):
        return [], enumerate(value.items)
    return default_enter(path, key, value)


def test_research_default_does_not_traverse_custom():
    root = {'a': Box([1, 2])}
    res = research(root, query=lambda p, k, v: v == 1)
    assert res == []


def test_research_custom_enter_traverses():
    root = {'a': Box([1, {'b': 2}])}
    res = research(root, query=lambda p, k, v: isinstance(v, int), enter=box_enter)
    assert sorted(res) == [(('a', 0), 1), (('a', 1, 'b'), 2)]


def test_research_enter_still_queries_and_default_behaviour():
    root = {'a': [1, 2]}
    res = research(root, query=lambda p, k, v: v == 2, enter=default_enter)
    assert res == [(('a', 1), 2)]
    assert research(root) == research(root, enter=default_enter)


def test_research_reraise_with_enter():
    def q(p, k, v):
        raise ValueError('x')
    assert research([1], q, enter=default_enter) == []
    with pytest.raises(ValueError):
        research([1], q, reraise=True, enter=default_enter)


def test_remap_trace(capsys):
    remap({'a': [1]}, visit=lambda p, k, v: (k, v), trace=True)
    out = capsys.readouterr().out
    assert 'remap enter:' in out and 'remap exit:' in out and 'remap visit:' in out


def test_remap_trace_selected(capsys):
    remap({'a': [1]}, visit=lambda p, k, v: (k, v), trace=('exit',))
    out = capsys.readouterr().out
    assert 'remap exit:' in out
    assert 'remap enter:' not in out and 'remap visit:' not in out
    remap([1], trace='enter')
    assert 'remap enter:' in capsys.readouterr().out


def test_remap_trace_bad_type():
    with pytest.raises(TypeError):
        remap([1], trace=5)
