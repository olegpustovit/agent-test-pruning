import pytest

from tomlkit import loads
from tomlkit.exceptions import ParseError


@pytest.mark.parametrize(
    "src",
    [
        "a = [1, @]",
        "a = [@]",
        "a = [1, 2, =]",
        "a = [1 2]",
        "a = [,]",
        "a = [1,,2]",
        "a = [\n  1,\n  !\n]",
    ],
)
def test_malformed_array_element_raises(src):
    with pytest.raises(ParseError):
        loads(src)


@pytest.mark.parametrize(
    "src",
    ["a = []", "a = [ ]", "a = [1, 2,]", "a = [1, 2, ]", "a = [\n 1,\n # c\n]\n"],
)
def test_valid_arrays_still_parse(src):
    assert loads(src).as_string() == src
