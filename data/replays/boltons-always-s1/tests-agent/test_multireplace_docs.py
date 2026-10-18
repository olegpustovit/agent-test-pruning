import importlib

from boltons import strutils


def test_docstrings_reference_real_module():
    for obj in (strutils.MultiReplace, strutils.multi_replace):
        assert 'stringutils' not in obj.__doc__
        assert 'strutils' in obj.__doc__
    # the documented module actually exists
    importlib.import_module('boltons.strutils')
    try:
        importlib.import_module('boltons.stringutils')
    except ImportError:
        pass
    else:
        raise AssertionError('boltons.stringutils should not exist')


def test_documented_examples():
    text = 'The foo bar cat ate a bat'
    expected = 'The zoo bar hat ate a kraken'
    m = strutils.MultiReplace({'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'})
    assert m.sub(text) == expected
    m = strutils.MultiReplace([('foo', 'zoo'), ('cat', 'hat'), ('bat', 'kraken')])
    assert m.sub(text) == expected
    from boltons.strutils import multi_replace
    assert multi_replace(text, {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}) == expected
