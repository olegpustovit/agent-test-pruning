from tomlkit import item, parse


def test_bool_items_compare_by_value():
    assert item(True) == item(True)
    assert item(False) == item(False)
    assert item(True) != item(False)


def test_bool_item_vs_plain_bool_and_other():
    assert item(True) == True  # noqa: E712
    assert item(False) != True  # noqa: E712
    assert item(True) != 1
    assert item(True) != "true"


def test_parsed_bools_compare():
    doc = parse("a = true\nb = true\nc = false\n")
    assert doc["a"] == doc["b"]
    assert doc["a"] != doc["c"]
