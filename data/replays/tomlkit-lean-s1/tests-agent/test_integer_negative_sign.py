import tomlkit


def test_negative_integer_times_minus_one():
    doc = tomlkit.parse("a = -5")
    result = doc["a"] * -1
    assert result == 5
    assert result.as_string() == "+5"


def test_negative_integer_times_two_has_single_minus():
    doc = tomlkit.parse("a = -5")
    assert (doc["a"] * 2).as_string() == "-10"


def test_signed_integer_becomes_negative():
    doc = tomlkit.parse("a = +5")
    result = doc["a"] * -1
    assert result == -5
    assert result.as_string() == "-5"


def test_signed_integer_stays_plus():
    doc = tomlkit.parse("a = +5")
    assert (doc["a"] + 1).as_string() == "+6"


def test_negative_integer_stays_single_minus():
    doc = tomlkit.parse("a = -5")
    assert (doc["a"] - 1).as_string() == "-6"
