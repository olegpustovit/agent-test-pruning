import pytest

import tomlkit

from tomlkit.items import Bool


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("true", True), ("false", False), (True, True), (False, False)],
)
def test_boolean_accepts_str_and_bool(raw, expected):
    b = tomlkit.boolean(raw)
    assert isinstance(b, Bool)
    assert b.value is expected
    assert b.as_string() == ("true" if expected else "false")


def test_boolean_bool_in_document():
    doc = tomlkit.document()
    doc["a"] = tomlkit.boolean(False)
    doc["b"] = tomlkit.boolean(True)
    assert tomlkit.dumps(doc) == "a = false\nb = true\n"
