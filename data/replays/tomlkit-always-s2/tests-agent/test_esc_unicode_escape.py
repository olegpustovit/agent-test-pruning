import tomllib

import tomlkit

from tomlkit._utils import escape_string


def test_escape_string_esc_uses_unicode_escape():
    assert escape_string("a\x1bb") == "a\\u001bb"


def test_dumps_esc_roundtrip_with_tomllib():
    doc = tomlkit.document()
    doc["k"] = "x\x1b[0m"
    out = tomlkit.dumps(doc)
    assert "\\e" not in out
    assert "\\u001b" in out
    assert tomllib.loads(out)["k"] == "x\x1b[0m"


def test_other_escapes_unchanged():
    assert escape_string("\n\t\\\"") == '\\n\\t\\\\\\"'
