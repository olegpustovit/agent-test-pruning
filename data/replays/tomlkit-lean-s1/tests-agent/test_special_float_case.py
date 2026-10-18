import math

import pytest

from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


@pytest.mark.parametrize(
    "literal", ["INF", "Inf", "iNf", "+INF", "-Inf", "NAN", "NaN", "+NaN", "-NAN"]
)
def test_non_lowercase_special_floats_rejected(literal):
    with pytest.raises(TOMLKitError):
        parse(f"a = {literal}")


def test_lowercase_special_floats_accepted():
    doc = parse("a = inf\nb = -inf\nc = +inf\nd = nan\ne = -nan")
    assert doc["a"] == math.inf
    assert doc["b"] == -math.inf
    assert doc["c"] == math.inf
    assert math.isnan(doc["d"])
    assert math.isnan(doc["e"])
