import pytest

import tomlkit

from tomlkit.items import SingleKey


@pytest.mark.parametrize("bad", [1, 1.5, None, b"a", ("a",), True])
def test_single_key_rejects_non_str(bad):
    with pytest.raises(TypeError, match="Keys must be strings"):
        SingleKey(bad)


def test_single_key_accepts_str():
    assert SingleKey("a").key == "a"
    assert SingleKey("a b").key == "a b"


def test_table_int_key_raises():
    doc = tomlkit.document()
    with pytest.raises(TypeError):
        doc[1] = 2
