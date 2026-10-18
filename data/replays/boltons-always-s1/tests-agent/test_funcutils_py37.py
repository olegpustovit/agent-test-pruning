import asyncio
import inspect

from boltons.funcutils import (CachedInstancePartial, FunctionBuilder,
                               inspect_formatargspec)


def test_formatargspec_basic():
    assert inspect_formatargspec(['a', 'b'], defaults=(1,)) == '(a, b=1)'


def test_formatargspec_full():
    s = inspect_formatargspec(
        ['a', 'b'], varargs='args', varkw='kw', defaults=(2,),
        kwonlyargs=['k'], kwonlydefaults={'k': 'x'},
        annotations={'a': int, 'return': str})
    assert s == "(a: int, b=2, *args, k='x', **kw) -> str"


def test_formatargspec_kwonly_star_and_empty():
    assert inspect_formatargspec([], kwonlyargs=['k']) == '(*, k)'
    assert inspect_formatargspec([]) == '()'


def test_formatargspec_matches_signature():
    def f(a, b=1, *args, c, d=3, **kw): pass
    spec = inspect.getfullargspec(f)
    s = inspect_formatargspec(*spec)
    assert s == '(a, b=1, *args, c, d=3, **kw)'


def test_cached_instance_partial_set_name():
    class A:
        def __init__(self):
            self.v = 5

        def m(self, x, y):
            return self.v + x + y
        pm = CachedInstancePartial(m, 1)

    assert A.__dict__['pm'].__name__ == 'pm'
    a = A()
    assert a.pm(2) == 8
    assert a.pm is a.pm
    assert a.__dict__['pm'] is a.pm
    assert A.pm is not None


def test_functionbuilder_async_detection():
    async def coro(a, b=1):
        return a

    fb = FunctionBuilder.from_func(coro)
    assert fb.is_async
    f = fb.get_func()
    assert inspect.iscoroutinefunction(f)
    assert asyncio.run(f(4)) == 4


def test_functionbuilder_sync_not_async():
    def g(a): return a
    assert not FunctionBuilder.from_func(g).is_async
