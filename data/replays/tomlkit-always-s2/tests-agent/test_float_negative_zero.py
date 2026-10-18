from tomlkit import dumps, parse
from tomlkit.items import Float


def test_signed_float_times_zero_negative_zero():
    doc = parse("a = -1.5\n")
    doc["a"] = doc["a"] * 0
    out = dumps(doc)
    assert out == "a = -0.0\n"
    assert parse(out)["a"] == 0.0


def test_positive_signed_float_keeps_plus():
    doc = parse("a = +1.5\n")
    doc["a"] = doc["a"] * 2
    assert dumps(doc) == "a = +3.0\n"


def test_signed_float_zero_result_keeps_plus():
    doc = parse("a = +1.5\n")
    doc["a"] = doc["a"] * 0
    assert dumps(doc) == "a = +0.0\n"


def test_negative_float_stays_negative():
    f = parse("a = -1.5\n")["a"]
    assert isinstance(f, Float)
    assert (f * 2).as_string() == "-3.0"
