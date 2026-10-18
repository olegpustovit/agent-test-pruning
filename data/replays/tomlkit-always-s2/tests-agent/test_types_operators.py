from __future__ import annotations

import tomlkit._types as types

from tomlkit import array
from tomlkit import table
from tomlkit.items import Table


def test_wrap_method_removed():
    assert not hasattr(types, "wrap_method")
    assert "wrap_method" not in types.__all__


def test_all_exports_exist():
    for name in types.__all__:
        assert hasattr(types, name)


def test_custom_list_add_and_iadd():
    a = array("[1, 2]")
    result = a + [3, 4]
    assert list(result) == [1, 2, 3, 4]
    assert list(a) == [1, 2]

    a += [5]
    assert list(a) == [1, 2, 5]


def test_custom_dict_or_and_ior():
    t = table()
    t["a"] = 1
    result = t | {"b": 2}
    assert isinstance(result, Table)
    assert dict(result) == {"a": 1, "b": 2}
    assert "b" not in t

    t |= {"c": 3}
    assert dict(t) == {"a": 1, "c": 3}
