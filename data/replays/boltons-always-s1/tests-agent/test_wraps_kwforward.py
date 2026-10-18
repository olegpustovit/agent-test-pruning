from boltons.funcutils import wraps, FunctionBuilder


def _spy():
    seen = {}

    def deco(f):
        @wraps(f)
        def w(*args, **kwargs):
            seen['args'] = args
            seen['kwargs'] = kwargs
            return f(*args, **kwargs)
        return w
    return seen, deco


def inv(f):
    return FunctionBuilder.from_func(f).get_invocation_str()


def test_invocation_str_plain():
    def f(a, b): pass
    assert inv(f) == 'a, b'


def test_invocation_str_defaults_keyword():
    def f(a, b=1, c=2): pass
    assert inv(f) == 'a, b=b, c=c'


def test_invocation_str_kwonly_and_varkw():
    def f(a, *, k, j=3, **kw): pass
    assert inv(f) == 'a, k=k, j=j, **kw'


def test_invocation_str_varargs_keeps_positional():
    def f(a, b=1, *args, k=2, **kw): pass
    assert inv(f) == 'a, b, *args, k=k, **kw'


def test_invocation_str_posonly():
    def f(a, b=1, /, c=2, d=3): pass
    assert inv(f) == 'a, b, c=c, d=d'


def test_invocation_str_posonly_all_defaulted():
    def f(a=1, /, b=2): pass
    assert inv(f) == 'a, b=b'


def test_defaults_land_in_kwargs():
    seen, deco = _spy()

    @deco
    def f(a, b=2, *, k=3):
        return (a, b, k)

    assert f(1) == (1, 2, 3)
    assert seen['args'] == (1,)
    assert seen['kwargs'] == {'b': 2, 'k': 3}
    assert f(1, 5, k=7) == (1, 5, 7)
    assert seen['kwargs'] == {'b': 5, 'k': 7}


def test_posonly_works():
    seen, deco = _spy()

    @deco
    def f(a, b=2, /, c=3):
        return (a, b, c)

    assert f(1) == (1, 2, 3)
    assert seen['args'] == (1, 2)
    assert seen['kwargs'] == {'c': 3}


def test_varargs_with_defaults():
    seen, deco = _spy()

    @deco
    def f(a, b=2, *args, k=4):
        return (a, b, args, k)

    assert f(1, 2, 3, 4) == (1, 2, (3, 4), 4)
    assert f(1) == (1, 2, (), 4)
    assert seen['kwargs'] == {'k': 4}


def test_wraps_issue_261_kwonly_vs_default():
    def f(a, *, b):
        return (a, b)

    def g(a, b=5):
        return (a, b)

    w = wraps(g)(f)
    assert w(1, b=2) == (1, 2)
    assert w(1) == (1, 5)


def test_partial_no_code():
    import functools

    def f(a, b, c=3):
        return (a, b, c)

    p = functools.partial(f, 1)
    fb = FunctionBuilder.from_func(p)
    assert fb.posonlyargs == []
