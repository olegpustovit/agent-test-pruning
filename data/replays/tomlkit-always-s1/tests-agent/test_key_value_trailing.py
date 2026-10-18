import pytest

import tomlkit

from tomlkit.exceptions import UnexpectedCharError


@pytest.mark.parametrize(
    "src",
    [
        "a = 1 b = 2 c = 3",
        "a = 1 b = 2",
        "a = 1\nb = 2",
        "a = 1 # c\nb = 2",
        "a = 1\n\n[t]",
        "a = 1 x",
    ],
)
def test_key_value_rejects_trailing(src):
    with pytest.raises(UnexpectedCharError):
        tomlkit.key_value(src)


@pytest.mark.parametrize(
    "src",
    ["a = 1", "a = 1  ", "a = 1\n", "a = 1 # comment", "a = 1 # comment\n", "a = 1\r\n"],
)
def test_key_value_accepts_trailing_ws_and_comment(src):
    k, v = tomlkit.key_value(src)
    assert k.key == "a"
    assert v == 1


def test_key_value_string_value():
    k, v = tomlkit.key_value('a = "x y"')
    assert (k.key, v) == ("a", "x y")
