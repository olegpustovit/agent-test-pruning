from tomlkit.items import item


def test_inline_table_in_nested_list_preserves_order():
    assert item([[{"a": {"x": 1}, "b": 2}]]).as_string() == "[[{a = {x = 1}, b = 2}]]"


def test_inline_table_sort_keys_purely_alphabetical():
    v = item({"k": [1, {"b": 1, "a": {"x": 1}, "c": 2}]}, _sort_keys=True)
    assert v.as_string().strip() == "k = [1, {a = {x = 1}, b = 1, c = 2}]"


def test_aot_dict_values_still_last():
    out = item([{"a": {"x": 1}, "b": 2}]).as_string()
    assert out.index("b = 2") < out.index("a")
