import pytest

from tomlkit import api
from tomlkit.items import Integer


@pytest.mark.parametrize(
    "raw, value",
    [
        ("1_000", 1000),
        ("+1_000", 1000),
        ("-1_0", -10),
        ("0", 0),
        ("-0", 0),
        ("42", 42),
        ("0xdead_beef", 0xDEADBEEF),
        ("0xDEAD", 0xDEAD),
        ("0o7_7", 0o77),
        ("0b1_0", 2),
    ],
)
def test_integer_string_preserved(raw, value):
    i = api.integer(raw)
    assert isinstance(i, Integer)
    assert i == value
    assert i.as_string() == raw
    assert api.dumps({"a": i}) == f"a = {raw}\n"


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "_1",
        "1_",
        "1__0",
        "01",
        "+01",
        "1.5",
        "abc",
        " 1",
        "1\n",
        "0X1F",
        "0O7",
        "0B1",
        "+0x1",
        "-0b1",
        "0x",
        "0x_1",
        "0xg",
        "0o8",
        "0b2",
        "0b1_",
    ],
)
def test_integer_invalid_string(raw):
    with pytest.raises(ValueError):
        api.integer(raw)


def test_integer_from_int_unchanged():
    assert api.integer(1000).as_string() == "1000"
    assert api.integer(-5).as_string() == "-5"
