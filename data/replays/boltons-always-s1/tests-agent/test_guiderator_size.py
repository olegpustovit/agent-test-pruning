import pytest

from boltons.iterutils import GUIDerator


@pytest.mark.parametrize('size', [19, 37, 0, -1])
def test_out_of_range_message_is_inclusive(size):
    with pytest.raises(ValueError, match=r'expected 20 <= size <= 36'):
        GUIDerator(size=size)


@pytest.mark.parametrize('size', [20, 36])
def test_boundary_sizes_accepted(size):
    g = GUIDerator(size=size)
    assert len(next(g)) == size
