import pytest

import tomlkit

from tomlkit.exceptions import UnexpectedCharError


@pytest.mark.parametrize("src", ["a = 1 b = 2 c = 3", "a = 1 b = 2", "a = 1\nb = 2", "a = 1 x"])
def test_key_value_rejects_trailing(src):
    with pytest.raises(UnexpectedCharError):
        tomlkit.key_value(src)


@pytest.mark.parametrize("src", ["a = 1", "a = 1   ", "a = 1 # c", "a = 1\n", "a = 1 # c\n"])
def test_key_value_accepts_trailing_ws_comment(src):
    k, v = tomlkit.key_value(src)
    assert k.key == "a"
    assert v == 1
