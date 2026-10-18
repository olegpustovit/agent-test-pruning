from tomlkit import dumps
from tomlkit import parse
from tomlkit.items import Array
from tomlkit.items import item
from tomlkit.toml_document import TOMLDocument
from tomlkit.items import Trivia


def _inline(value, sort_keys=False):
    return item(value, _parent=Array([], Trivia()), _sort_keys=sort_keys).as_string()


def test_inline_table_preserves_insertion_order():
    assert item([[{"a": {"x": 1}, "b": 2}]]).as_string() == "[[{a = {x = 1}, b = 2}]]"
    assert _inline([{"b": 1, "a": {"x": 1}, "c": 2}]) == "[{b = 1, a = {x = 1}, c = 2}]"


def test_inline_table_sort_keys_is_purely_alphabetical():
    out = _inline([{"b": 1, "a": {"x": 1}, "c": 2}], sort_keys=True)
    assert out == "[{a = {x = 1}, b = 1, c = 2}]"
    out = _inline([{"z": {"x": 1}, "b": 2}], sort_keys=True)
    assert out == "[{b = 2, z = {x = 1}}]"


def test_aot_still_puts_dict_values_last():
    out = dumps({"t": [{"a": {"x": 1}, "b": 2}]})
    assert out.index("b = 2") < out.index("[t.a]")
    assert parse(out) == {"t": [{"a": {"x": 1}, "b": 2}]}


def test_aot_sort_keys_dicts_last():
    out = dumps({"t": [{"z": 1, "b": {"x": 1}, "a": 2}]}, sort_keys=True)
    assert out.index("a = 2") < out.index("z = 1") < out.index("[t.b]")
