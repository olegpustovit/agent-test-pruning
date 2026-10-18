import boltons.formatutils as formatutils
import boltons.funcutils as funcutils
import boltons.iterutils as iterutils


def test_formatutils_module_doc_spelling():
    assert 'programmatic' in formatutils.__doc__
    assert 'progammatic' not in formatutils.__doc__


def test_update_wrapper_doc_spelling():
    doc = funcutils.update_wrapper.__doc__
    assert 'does not modify anything in place' in doc
    assert 'modifiy' not in doc


def test_remap_doc_spelling():
    doc = iterutils.remap.__doc__
    assert 'heterogeneous' in doc
    assert 'heterogenous' not in doc


def test_untyped_sorted_doc_spelling():
    doc = iterutils.untyped_sorted.__doc__
    assert 'heterogeneous' in doc
    assert 'heterogenous' not in doc


def test_untyped_sorted_still_works():
    assert iterutils.untyped_sorted(['abc', 2.0, 1, 2, 'def']) == [1, 2, 2.0, 'abc', 'def']
