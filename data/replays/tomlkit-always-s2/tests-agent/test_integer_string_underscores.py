import pytest

import tomlkit

from tomlkit import api


@pytest.mark.parametrize(
    "raw, value",
    [
        ("1_000", 1000),
        ("1_000_000", 1000000),
        ("+1_000", 1000),
        ("-1_0", -10),
        ("0", 0),
        ("-0", 0),
        ("+0", 0),
        ("42", 42),
        ("0xdead_beef", 0xDEADBEEF),
        ("0xDEAD", 0xDEAD),
        ("0o7_7", 0o77),
        ("0b1_0", 2),
    ],
)
def test_integer_string_preserved(raw, value):
    i = api.integer(raw)
    assert i == value
    assert i.as_string() == raw
    doc = tomlkit.document()
    doc["a"] = i
    assert doc.as_string() == f"a = {raw}\n"
    assert tomlkit.parse(doc.as_string())["a"] == value


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "_1",
        "1_",
        "1__0",
        "01",
        "00",
        "+0x1",
        "-0b1",
        "0X1F",
        "0B1",
        "0O7",
        "0x",
        "0x_1",
        "0b2",
        "0o8",
        "1.5",
        "1e3",
        " 1",
        "1 ",
        "1\n",
        "abc",
        "++1",
    ],
)
def test_integer_string_invalid(raw):
    with pytest.raises(ValueError):
        api.integer(raw)


def test_integer_from_int_unchanged():
    assert api.integer(1000).as_string() == "1000"
    assert api.integer(-5).as_string() == "-5"
