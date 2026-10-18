import pytest

from boltons.dictutils import OneToOne


def test_update_empty_dict():
    ot = OneToOne({'a': 1})
    ot.update({})
    assert ot == {'a': 1}
    assert ot.inv == {1: 'a'}


def test_update_empty_list():
    ot = OneToOne()
    ot.update([])
    assert ot == {} and ot.inv == {}


def test_update_empty_tuple_and_iterable_with_kwargs():
    ot = OneToOne()
    ot.update((), a=1)
    ot.update([], b=2)
    assert ot == {'a': 1, 'b': 2}
    assert ot.inv == {1: 'a', 2: 'b'}


def test_update_empty_dict_with_kwargs():
    ot = OneToOne()
    ot.update({}, x=5)
    assert ot == {'x': 5}
    assert ot.inv == {5: 'x'}


def test_update_nonempty_still_works():
    ot = OneToOne()
    ot.update([('a', 1), ('b', 2)])
    ot.update({'c': 3}, d=4)
    assert ot == {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    assert ot.inv == {1: 'a', 2: 'b', 3: 'c', 4: 'd'}


def test_update_unhashable_value_rejected():
    ot = OneToOne({'a': 1})
    with pytest.raises(TypeError):
        ot.update({'b': []})
    assert ot == {'a': 1}
