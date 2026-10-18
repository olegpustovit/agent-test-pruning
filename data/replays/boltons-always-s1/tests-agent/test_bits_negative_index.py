import pytest
from boltons.mathutils import Bits


def test_negative_index_matches_positive():
    b = Bits('1011')
    for i in range(4):
        assert b[i - 4] == b[i]
    assert b[-1] is True
    assert b[-2] is True
    assert b[-3] is False
    assert b[-4] is True


def test_negative_index_last_bit_zero():
    assert Bits('10')[-1] is False


@pytest.mark.parametrize('k', [-5, -100, 4, 100])
def test_out_of_range(k):
    with pytest.raises(IndexError):
        Bits('1011')[k]


def test_negative_slice():
    assert Bits('1011')[-2:].as_bin() == '11'
