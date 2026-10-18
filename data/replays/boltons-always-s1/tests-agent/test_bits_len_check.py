import pytest

from boltons.mathutils import Bits


def test_value_equal_to_two_pow_len_rejected():
    with pytest.raises(ValueError):
        Bits(4, 2)
    with pytest.raises(ValueError):
        Bits(1, 0)
    with pytest.raises(ValueError):
        Bits(256, 8)


def test_max_value_accepted():
    for n in (1, 2, 4, 8):
        b = Bits(2 ** n - 1, n)
        assert len(b) == n
        assert b.as_bin() == '1' * n


def test_len_getitem_invariant_and_roundtrip():
    b = Bits(3, 2)
    assert len(b) == 2
    assert list(b) == [True, True]
    assert Bits(b.as_bin()) == b


def test_auto_length_never_trips():
    for v in (0, 1, 2, 3, 4, 255, 256, 2 ** 40):
        assert Bits(v).val == v
