from boltons.setutils import complement


def dc(*items):
    return complement(complement(set(items)))


def test_ge_double_complement():
    assert dc(1, 2) >= dc(1)
    assert dc(1, 2) >= dc(1, 2)
    assert not (dc(1) >= dc(1, 2))
    assert not (dc(1, 2) >= dc(3))


def test_le_double_complement():
    assert dc(1) <= dc(1, 2)
    assert dc(1) <= dc(1)
    assert not (dc(1, 2) <= dc(1))


def test_lt_gt_double_complement():
    assert dc(1) < dc(1, 2)
    assert not (dc(1) < dc(1))
    assert dc(1, 2) > dc(1)
    assert not (dc(1) > dc(1))


def test_not_implemented_for_foreign_types():
    c = complement({1})
    assert c.__le__(5) is NotImplemented
    assert c.__lt__(5) is NotImplemented
    assert c.__ge__(5) is NotImplemented
