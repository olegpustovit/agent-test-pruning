import pytest

from tomlkit import inline_table
from tomlkit import table


def test_add_table_to_inline_table_raises():
    it = inline_table()
    with pytest.raises(ValueError, match="cannot contain a table"):
        it.append("a", table())
    assert it.as_string() == "{}"


def test_setitem_table_on_inline_table_raises():
    it = inline_table()
    with pytest.raises(ValueError, match="cannot contain a table"):
        it["a"] = table()
    it["b"] = 1
    assert it.as_string() == "{b = 1}"
