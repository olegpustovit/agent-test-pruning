import pytest

import tomlkit


@pytest.mark.parametrize(
    "raw, value",
    [
        ("1_000", 1000),
        ("-1_000", -1000),
        ("+1_0", 10),
        ("0xdead_beef", 0xDEADBEEF),
        ("0o7_7", 0o77),
        ("0b1_0", 2),
        ("0", 0),
        ("34", 34),
    ],
)
def test_integer_string_preserved(raw, value):
    i = tomlkit.integer(raw)
    assert i == value
    assert i.as_string() == raw
    doc = tomlkit.document()
    doc["a"] = i
    assert tomlkit.dumps(doc) == f"a = {raw}\n"


@pytest.mark.parametrize(
    "raw",
    ["", "_1", "1_", "1__0", "01", "0X1f", "+0x1", "-0b1", "0x", "0b2", "0o8", "1.0", " 1", "abc", "0x_1"],
)
def test_integer_string_invalid(raw):
    with pytest.raises(ValueError):
        tomlkit.integer(raw)


def test_integer_int_unchanged():
    assert tomlkit.integer(1000).as_string() == "1000"
