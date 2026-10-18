from boltons.funcutils import wraps, FunctionBuilder


def test_undefaulted_positional_to_kwonly():
    def g(a, b): pass

    def f(a, *, b):
        return (a, b)

    assert wraps(g)(f)(1, 2) == (1, 2)
    assert wraps(g)(f)(1, b=2) == (1, 2)


def test_varargs_flavor():
    def g(a, *va, b): pass

    def f(a, *va, b):
        return (a, va, b)

    assert wraps(g)(f)(1, 5, 6, b=2) == (1, (5, 6), 2)


def test_varargs_donor_positional_b():
    def g(a, b, *va): pass

    def f(a, *va, b):
        return (a, va, b)

    assert wraps(g)(f)(1, 2) == (1, (), 2)


def test_invocation_str_target():
    fb = FunctionBuilder.from_func(lambda a, b: None)

    def t(a, *, b): pass

    assert fb.get_invocation_str() == 'a, b'
    assert fb.get_invocation_str(target=t) == 'a, b=b'


def test_uninspectable_target_falls_back():
    class Bad:
        @property
        def __signature__(self):
            raise ValueError

        def __call__(self, *a): pass

    fb = FunctionBuilder.from_func(lambda a, b: None)
    assert fb.get_invocation_str(target=Bad()) == 'a, b'
