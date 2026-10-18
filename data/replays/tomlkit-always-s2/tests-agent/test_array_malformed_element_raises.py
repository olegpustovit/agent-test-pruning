import pytest

from tomlkit import parse
from tomlkit.exceptions import ParseError


@pytest.mark.parametrize(
    "src",
    ["a = [1, @]", "a = [1 2]", "a = [,]", "a = [1,,2]", "a = [1, 2", "a = [@]"],
)
def test_malformed_array_raises(src):
    with pytest.raises(ParseError):
        parse(src)


@pytest.mark.parametrize("src", ["a = [1, 2,]", "a = [ ]", "a = [\n1,\n# c\n2\n]"])
def test_valid_arrays_still_parse(src):
    parse(src)
