import pytest

from boltons.strutils import bytes2human


@pytest.mark.parametrize('nbytes, expected', [
    (0, '0B'),
    (1, '1B'),
    (1023, '1023B'),
    (1024, '1K'),
    (1025, '1K'),
    (1024 ** 2 - 1, '1024K'),
    (1024 ** 2, '1M'),
    (1024 ** 3, '1G'),
    (1024 ** 4, '1T'),
    (1024 ** 5, '1P'),
    (1024 ** 6, '1E'),
    (1024 ** 7, '1Z'),
    (-1023, '-1023B'),
    (-1024, '-1K'),
    (-1024 ** 2, '-1M'),
])
def test_exact_boundaries(nbytes, expected):
    assert bytes2human(nbytes) == expected


def test_ndigits_at_boundary():
    assert bytes2human(1024, 2) == '1.00K'
    assert bytes2human(1024 ** 2, 1) == '1.0M'
    assert bytes2human(0, 2) == '0.00B'


def test_mid_range_unchanged():
    assert bytes2human(1536, 1) == '1.5K'
    assert bytes2human(100 * 1024 ** 2) == '100M'
