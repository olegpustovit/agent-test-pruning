import math

import pytest

from tomlkit import parse
from tomlkit.exceptions import ParseError


@pytest.mark.parametrize("val", ["inf", "+inf", "-inf"])
def test_lowercase_inf(val):
    assert parse(f"a = {val}")["a"] == float(val)


@pytest.mark.parametrize("val", ["nan", "+nan", "-nan"])
def test_lowercase_nan(val):
    assert math.isnan(parse(f"a = {val}")["a"])


@pytest.mark.parametrize(
    "val", ["INF", "Inf", "iNf", "+INF", "-Inf", "NAN", "NaN", "+NaN", "-NAN"]
)
def test_non_lowercase_rejected(val):
    with pytest.raises(ParseError):
        parse(f"a = {val}")
