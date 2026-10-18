from boltons.setutils import complement, _ComplementSet


def test_le_both_complements():
    # - - branch: ~a <= ~b iff a >= b
    assert complement({1}) <= complement({1})
    assert complement({1, 2}) <= complement({1})
    assert not (complement({1}) <= complement({1, 2}))


def test_ge_both_complements():
    # + + branch via included sets
    a = _ComplementSet(included={1, 2})
    b = _ComplementSet(included={1})
    assert a >= b
    assert not (b >= a)
