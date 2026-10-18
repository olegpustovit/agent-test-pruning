import pytest

from tomlkit import document
from tomlkit.items import SingleKey


@pytest.mark.parametrize("key", [1, None, 1.5, b"a", ("a",)])
def test_single_key_rejects_non_string(key):
    with pytest.raises(TypeError, match="Keys must be strings"):
        SingleKey(key)


def test_table_setitem_int_key_rejected():
    doc = document()
    with pytest.raises(TypeError):
        doc[1] = "x"


def test_single_key_accepts_string():
    assert SingleKey("a").key == "a"
