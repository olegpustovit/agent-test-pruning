from boltons.dictutils import OMD


def test_ior_dict_returns_self_and_overwrites():
    omd = OMD([('a', 1), ('a', 2), ('b', 3)])
    orig = omd
    omd |= {'a': 9, 'c': 4}
    assert omd is orig
    assert omd.getlist('a') == [9]
    assert omd['b'] == 3
    assert omd['c'] == 4


def test_ior_omd_keeps_multi_values():
    omd = OMD([('a', 1), ('b', 2)])
    omd |= OMD([('a', 5), ('a', 6)])
    assert omd.getlist('a') == [5, 6]
    assert omd.getlist('b') == [2]


def test_ior_iterable_of_pairs():
    omd = OMD([('a', 1)])
    omd |= [('a', 2), ('a', 3), ('d', 4)]
    assert omd.getlist('a') == [2, 3]
    assert omd['d'] == 4


def test_ior_self():
    omd = OMD([('a', 1), ('a', 2)])
    omd |= omd
    assert omd.getlist('a') == [1, 2]
