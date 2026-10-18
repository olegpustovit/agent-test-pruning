import tomlkit


def _roundtrip(doc):
    text = doc.as_string()
    assert tomlkit.parse(text).as_string() == text
    return text


def test_signed_float_times_zero_is_negative_zero():
    doc = tomlkit.parse("a = -1.5\n")
    doc["a"] = doc["a"] * 0
    text = _roundtrip(doc)
    assert text == "a = -0.0\n"


def test_explicit_plus_float_times_negative_zero():
    doc = tomlkit.parse("a = +1.5\n")
    doc["a"] = doc["a"] * -1 * 0
    text = _roundtrip(doc)
    assert "+-" not in text
    assert text == "a = -0.0\n"


def test_explicit_plus_still_added_for_positive_and_zero():
    doc = tomlkit.parse("a = +1.5\n")
    assert (doc["a"] * 2).as_string() == "+3.0"
    assert (doc["a"] * 0).as_string() == "+0.0"


def test_unsigned_float_no_plus():
    doc = tomlkit.parse("a = 1.5\n")
    assert (doc["a"] * 2).as_string() == "3.0"


def test_negative_result_keeps_single_minus():
    doc = tomlkit.parse("a = +1.5\n")
    assert (doc["a"] * -2).as_string() == "-3.0"
