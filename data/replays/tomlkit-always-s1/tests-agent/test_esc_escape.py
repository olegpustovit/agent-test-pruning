import tomllib

import tomlkit

from tomlkit._utils import escape_string


def test_escape_string_writes_esc_as_unicode():
    assert escape_string("a\x1bb") == "a\\u001bb"


def test_other_compact_escapes_unchanged():
    assert escape_string("\n\t\b\f\r") == "\\n\\t\\b\\f\\r"


def test_esc_string_roundtrip_with_tomllib():
    doc = tomlkit.document()
    doc["k"] = "x\x1by"
    out = tomlkit.dumps(doc)
    assert "\\e" not in out
    assert "\\u001b" in out
    assert tomllib.loads(out)["k"] == "x\x1by"
    assert tomlkit.loads(out)["k"] == "x\x1by"


def test_parsing_backslash_e_still_works():
    assert tomlkit.loads('k = "a\\eb"')["k"] == "a\x1bb"
