from tomlkit import dumps
from tomlkit import parse


TEXT = "[a]\n[ a . b ]\nx=1\n"


def test_self_assignment_preserves_child_display_name():
    doc = parse(TEXT)
    doc["a"]["b"] = doc["a"]["b"]
    assert dumps(doc) == TEXT


def test_self_assignment_preserves_display_name_of_nested_header():
    doc = parse(TEXT)
    doc["a"] = doc["a"]
    assert dumps(doc) == TEXT
