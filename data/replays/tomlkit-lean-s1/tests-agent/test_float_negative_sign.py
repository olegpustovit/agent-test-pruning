from tomlkit import parse


def test_signed_float_becomes_negative():
    doc = parse("float = +1.5")
    doc["float"] -= 3
    assert doc["float"] == -1.5
    assert doc.as_string() == "float = -1.5"


def test_negative_float_stays_single_minus():
    doc = parse("float = -1.5")
    doc["float"] -= 1
    assert doc.as_string() == "float = -2.5"


def test_signed_float_stays_plus():
    doc = parse("float = +1.5")
    doc["float"] += 1
    assert doc.as_string() == "float = +2.5"


def test_negative_zero_result_has_no_plus():
    doc = parse("a = -1.5")
    doc["a"] *= 0
    assert doc.as_string() == "a = -0.0"
    assert parse(doc.as_string())["a"] == 0.0


def test_positive_zero_result_keeps_plus():
    doc = parse("a = +1.5")
    doc["a"] *= 0
    assert doc.as_string() == "a = +0.0"
