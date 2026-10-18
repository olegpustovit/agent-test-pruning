import pytest

from tomlkit import dumps
from tomlkit import item
from tomlkit import parse


@pytest.mark.parametrize(
    "src, factor, expected",
    [
        ("a = -5", -1, "+5"),
        ("a = 5", -1, "-5"),
        ("a = +5", -1, "-5"),
        ("a = -5", 1, "-5"),
        ("a = +5", 1, "+5"),
        ("a = +5", 2, "+10"),
        ("a = -5", 2, "-10"),
        ("a = 0", -1, "0"),
        ("a = +0", 1, "+0"),
    ],
)
def test_integer_mul_sign(src, factor, expected):
    v = parse(src)["a"] * factor
    assert v == int(expected)
    assert v.as_string() == expected


def test_negative_mul_no_double_minus():
    v = parse("a = -5")["a"] * -1
    assert v.as_string() == "+5"
    assert (parse("a = -5")["a"] * 3).as_string() == "-15"
    assert dumps(parse("a = -5")) == "a = -5"


def test_plain_integer_ops():
    assert (item(-3) * -1).as_string() == "+3"
    assert (item(3) * -1).as_string() == "-3"
    assert (parse("a = -5")["a"] + -1).as_string() == "-6"
