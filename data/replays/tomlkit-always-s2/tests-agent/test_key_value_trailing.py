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
        "a = 'x' junk",
        "a = 1 ]",
    ],
)
def test_key_value_rejects_trailing(src):
    with pytest.raises(UnexpectedCharError):
        tomlkit.key_value(src)


@pytest.mark.parametrize(
    "src",
    ["a = 1", "a = 1  ", "a = 1\n", "a = 1 # comment", "a = 1 # comment\n"],
)
def test_key_value_accepts_trailer(src):
    k, v = tomlkit.key_value(src)
    assert k.key == "a"
    assert v == 1


def test_key_value_matches_parse():
    with pytest.raises(UnexpectedCharError):
        tomlkit.parse("a = 1 b = 2")
    with pytest.raises(UnexpectedCharError):
        tomlkit.key_value("a = 1 b = 2")
