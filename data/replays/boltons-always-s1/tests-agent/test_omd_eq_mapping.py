import pytest

from boltons.dictutils import OrderedMultiDict as DOMD
from boltons.urlutils import OrderedMultiDict as UOMD


@pytest.mark.parametrize('cls', [DOMD, UOMD])
def test_eq_plain_mapping_values(cls):
    omd = cls([('a', 1), ('b', 2)])
    assert omd == {'a': 1, 'b': 2}
    assert not (omd == {'a': 999, 'b': 2})
    assert omd != {'a': 1, 'b': 3}
    assert omd != {'a': 1, 'c': 2}


@pytest.mark.parametrize('cls', [DOMD, UOMD])
def test_eq_plain_mapping_multi_uses_last_value(cls):
    omd = cls([('a', 1), ('a', 2)])
    assert omd == {'a': 2}
    assert omd != {'a': 1}
