import re
from boltons.statsutils import Stats
from boltons.iterutils import GUIDerator



def test_histogram_counts_exact():
    s = Stats([1, 1, 2, 5, 5, 5, 9])
    assert s.get_histogram_counts(bins=[0, 2, 5, 8]) == [(0, 2), (2, 1), (5, 3), (8, 1)]


def test_histogram_empty_bin_zero():
    s = Stats([1, 1, 10])
    assert s.get_histogram_counts(bins=[0, 4, 8]) == [(0, 2), (4, 0), (8, 1)]


def test_guiderator_salt_hex_and_unique():
    g = GUIDerator()
    assert re.search(r'-[0-9a-f]{12}$', g.salt)
    ids = [next(g) for _ in range(100)]
    assert len(set(ids)) == 100
    old = g.salt
    g.reseed()
    assert g.salt != old
