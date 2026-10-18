import pytest

from tomlkit import dumps
from tomlkit import parse


@pytest.mark.parametrize(
    "raw, op, expected",
    [
        ("+1.5", lambda x: x - 5, "-3.5"),
        ("+1.5", lambda x: x + 1, "+2.5"),
        ("-1.5", lambda x: x * 2, "-3.0"),
        ("-1.5", lambda x: x + 3, "+1.5"),
        ("1.5", lambda x: x - 5, "-3.5"),
    ],
)
def test_float_arithmetic_sign(raw, op, expected):
    doc = parse(f"a = {raw}")
    result = op(doc["a"])
    assert result.as_string() == expected
    doc["a"] = result
    assert dumps(doc) == f"a = {expected}"
    assert parse(dumps(doc))["a"] == float(expected)
