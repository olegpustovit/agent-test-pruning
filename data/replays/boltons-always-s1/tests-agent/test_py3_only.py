from datetime import timedelta

import pytest

from boltons import timeutils, ioutils, funcutils
from boltons.dictutils import OMD


def test_total_seconds():
    td = timedelta(days=4, seconds=33, microseconds=500000)
    assert timeutils.total_seconds(td) == td.total_seconds()


def test_omd_pickle_state_and_eq():
    import pickle
    o = OMD([('a', 1), ('a', 2), ('b', 3)])
    o2 = pickle.loads(pickle.dumps(o))
    assert o == o2
    assert list(o2.iteritems(multi=True)) == [('a', 1), ('a', 2), ('b', 3)]
    assert o != OMD([('a', 1)])


def test_spooled_type_errors():
    with pytest.raises(TypeError, match='bytes-like object is required'):
        ioutils.SpooledBytesIO().write('x')
    with pytest.raises(TypeError, match='str expected, got bytes'):
        ioutils.SpooledStringIO().write(b'x')


def test_function_builder_kwonly():
    fb = funcutils.FunctionBuilder('f', body='return a + b', args=['a'])
    fb.add_arg('b', 2, kwonly=True)
    f = fb.get_func()
    assert f(1) == 3
    with pytest.raises(funcutils.ExistingArgument):
        fb.add_arg('b', kwonly=True)


def test_instance_partial_method():
    class A:
        def m(x, self, y):
            return (type(self).__name__, x, y)
        p = funcutils.InstancePartial(m, 1)
    assert A().p(2) == ('A', 1, 2)
