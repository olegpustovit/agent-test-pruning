import math

from tomlkit import item


def test_float_ceil_floor():
    f = item(2.5)
    assert math.ceil(f) == 3
    assert math.floor(f) == 2
    assert math.ceil(item(-2.5)) == -2
    assert math.floor(item(-2.5)) == -3
