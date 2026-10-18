from tomlkit import dumps
from tomlkit import parse


def test_self_assign_preserves_display_name():
    s = "[keys .'a'.'c']\nx = 1\n"
    doc = parse(s)
    doc["keys"]["a"]["c"] = doc["keys"]["a"]["c"]
    assert dumps(doc) == s


def test_self_assign_top_level_table_preserves_header():
    s = "[ 'a' ]\nx = 1\n"
    doc = parse(s)
    doc["a"] = doc["a"]
    assert dumps(doc) == s

