import sys
import types

import pytest

from boltons.typeutils import make_sentinel


def test_module_scope_sets_module():
    s = make_sentinel('X', var_name='s')
    assert type(s).__module__ == __name__
    assert repr(s) == 's'
    assert not s


def test_no_var_name_no_module_requirement():
    s = make_sentinel('X')
    assert repr(s) == "Sentinel('X')"


def test_module_name_from_frame_globals():
    # a module registered in sys.modules, code exec'd with that __name__
    mod = types.ModuleType('_agent_fake_mod')
    sys.modules['_agent_fake_mod'] = mod
    try:
        exec('from boltons.typeutils import make_sentinel\n'
             'S = make_sentinel("S", var_name="S")', mod.__dict__)
        assert type(mod.S).__module__ == '_agent_fake_mod'
    finally:
        del sys.modules['_agent_fake_mod']


def test_unregistered_module_raises():
    g = {'__name__': '_agent_not_in_sys_modules'}
    with pytest.raises(ValueError):
        exec('from boltons.typeutils import make_sentinel\n'
             'make_sentinel("S", var_name="S")', g)


def test_missing_name_raises():
    g = {}
    with pytest.raises(ValueError):
        exec('from boltons.typeutils import make_sentinel\n'
             'make_sentinel("S", var_name="S")', g)
