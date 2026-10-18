import tomllib

import tomlkit


def test_esc_written_as_unicode_escape():
    doc = tomlkit.dumps({"a": "x\x1by"})
    assert doc == 'a = "x\\u001by"\n'
    assert tomllib.loads(doc) == {"a": "x\x1by"}
    assert tomlkit.loads(doc)["a"] == "x\x1by"
