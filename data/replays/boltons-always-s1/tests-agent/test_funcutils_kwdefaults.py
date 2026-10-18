from boltons.funcutils import copy_function


def test_copy_function_preserves_kwdefaults():
    def f(a, *, b=2, c=3):
        return a, b, c

    g = copy_function(f)
    assert g is not f
    assert g.__kwdefaults__ == {'b': 2, 'c': 3}
    assert g(1) == (1, 2, 3)
    assert g(1, b=5) == (1, 5, 3)


def test_copy_function_no_kwdefaults():
    def f(a, b=1):
        return a, b

    g = copy_function(f)
    assert g.__kwdefaults__ is None
    assert g(0) == (0, 1)
