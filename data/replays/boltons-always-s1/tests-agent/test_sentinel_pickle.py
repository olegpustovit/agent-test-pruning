import pickle

import pytest

from boltons.typeutils import make_sentinel

try:
    _PICKLE_ME = make_sentinel('pickle-me', var_name='_PICKLE_ME')
except ValueError as _exc:  # surfaced by the tests below
    _PICKLE_ME = None
    _CREATE_ERROR = _exc
else:
    _CREATE_ERROR = None


@pytest.fixture
def sentinel():
    assert _CREATE_ERROR is None, 'top-level make_sentinel(var_name=...) raised: %r' % _CREATE_ERROR
    return _PICKLE_ME


def test_pickle_roundtrip_returns_same_object(sentinel):
    for proto in range(pickle.HIGHEST_PROTOCOL + 1):
        assert pickle.loads(pickle.dumps(_PICKLE_ME, proto)) is _PICKLE_ME


def test_sentinel_module_set_to_caller_module(sentinel):
    assert type(_PICKLE_ME).__module__ == __name__
    assert repr(_PICKLE_ME) == '_PICKLE_ME'
    assert not _PICKLE_ME


def test_without_var_name_not_pickleable_and_no_error():
    s = make_sentinel('plain')
    assert repr(s) == "Sentinel('plain')"
    assert type(s).__module__ == 'boltons.typeutils'
    with pytest.raises(Exception):
        pickle.dumps(s)


def test_var_name_from_nonmodule_scope_still_works_or_raises_valueerror():
    # created in a function: either ValueError or a sentinel; never other error
    try:
        s = make_sentinel(var_name='_LOCAL')
    except ValueError:
        return
    assert repr(s) == '_LOCAL'
