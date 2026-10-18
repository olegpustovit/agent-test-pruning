import copy

from boltons.typeutils import make_sentinel

_S = make_sentinel('_S', var_name='_S')


def test_copy_returns_self():
    s = make_sentinel('x')
    assert copy.copy(s) is s


def test_copy_returns_self_with_var_name():
    assert copy.copy(_S) is _S


def test_copy_in_container_keeps_identity():
    s = make_sentinel('x')
    assert copy.copy([s])[0] is s


def test_deepcopy_returns_self():
    s = make_sentinel('x')
    assert copy.deepcopy(s) is s


def test_deepcopy_with_var_name():
    assert copy.deepcopy(_S) is _S


def test_deepcopy_in_container_keeps_identity():
    s = make_sentinel('x')
    assert copy.deepcopy({'k': [s]})['k'][0] is s


def test_deepcopy_direct_call_with_memo():
    s = make_sentinel('x')
    assert s.__deepcopy__({}) is s
