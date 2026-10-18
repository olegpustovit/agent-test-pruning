import pytest

from boltons.mathutils import Bits


def test_as_list_leading_zeros_preserved():
    assert Bits(0, 2).as_list() == [False, False]
    assert Bits(1, 4).as_list() == [False, False, False, True]


def test_as_list_matches_iteration_and_len():
    for val, n in [(0, 2), (1, 3), (5, 8), (0, 1), (255, 8)]:
        b = Bits(val, n)
        assert b.as_list() == list(b)
        assert len(b.as_list()) == len(b) == n


def test_as_list_default_length():
    assert Bits(5).as_list() == [True, False, True]


def test_list_roundtrip():
    b = Bits([False, False, True, False])
    assert b.as_list() == [False, False, True, False]
    assert Bits.from_list(b.as_list()) == b
