import pytest

from boltons.statsutils import Stats


def _pearson(skewness, kurtosis):
    # inject exact moments so branch boundaries are hit deterministically
    s = Stats([1.0, 2.0, 3.0])
    s._skewness = skewness
    s._kurtosis = kurtosis
    return s.pearson_type


def test_zero_c0_negative_c2_is_type_i():
    # beta1 = 4, beta2 = 3 -> c0 == 0 exactly, c1 = 12, c2 = -12
    assert _pearson(2.0, 3.0) == 1


@pytest.mark.parametrize('skew', [1.0, 2.0, 3.0, -2.0])
def test_zero_c0_never_raises(skew):
    # beta2 = 0.75 * beta1 -> c0 == 0; c2 is always negative here
    assert _pearson(skew, 0.75 * skew ** 2) == 1


def test_concrete_types():
    assert _pearson(1.0, 6.0) == 4   # k ~ 0.32
    assert _pearson(1.0, 5.0) == 5   # k ~ 0.94, rounds to 1 at precision 0
    assert _pearson(1.0, 4.8) == 6   # k ~ 1.56


def test_normal_and_gamma_precedence():
    assert _pearson(0.0, 3.0) == 0
    assert _pearson(1.0, 4.5) == 3   # c2 == 0
