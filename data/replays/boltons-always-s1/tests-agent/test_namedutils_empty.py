import pytest

from boltons.namedutils import namedtuple, namedlist


@pytest.mark.parametrize('factory', [namedtuple, namedlist])
def test_empty_field_name(factory):
    with pytest.raises(ValueError, match='non-empty'):
        factory('Point', ['x', ''])


@pytest.mark.parametrize('factory', [namedtuple, namedlist])
def test_empty_typename(factory):
    with pytest.raises(ValueError, match='non-empty'):
        factory('', ['x', 'y'])


@pytest.mark.parametrize('factory', [namedtuple, namedlist])
def test_rename_still_handles_empty(factory):
    cls = factory('Point', ['x', ''], rename=True)
    assert cls._fields == ('x', '_1')


@pytest.mark.parametrize('factory', [namedtuple, namedlist])
def test_valid_names_still_work(factory):
    cls = factory('Point', ['x', 'y'])
    assert cls._fields == ('x', 'y')
