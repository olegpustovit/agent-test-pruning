import math

import pytest

from tomlkit import loads
from tomlkit.exceptions import TOMLKitError


@pytest.mark.parametrize("lit", ["inf", "+inf", "-inf", "nan", "+nan", "-nan"])
def test_lowercase_special_floats_ok(lit):
    v = loads(f"a = {lit}")["a"]
    if "nan" in lit:
        assert math.isnan(v)
    else:
        assert math.isinf(v) and (v < 0) == lit.startswith("-")


@pytest.mark.parametrize(
    "lit", ["INF", "Inf", "iNf", "+INF", "-Inf", "NAN", "NaN", "+NaN", "-NAN"]
)
def test_non_lowercase_special_floats_rejected(lit):
    with pytest.raises(TOMLKitError):
        loads(f"a = {lit}")
