import pytest

import tomlkit

from tomlkit.items import String
from tomlkit.items import StringType


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        ('"basic"', StringType.SLB),
        ("'literal'", StringType.SLL),
        ('"""multi\nline"""', StringType.MLB),
        ("'''multi\nline'''", StringType.MLL),
    ],
)
def test_parsed_string_type(src, expected):
    doc = tomlkit.parse(f"a = {src}")
    assert isinstance(doc["a"], String)
    assert doc["a"].type is expected


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({}, StringType.SLB),
        ({"literal": True}, StringType.SLL),
        ({"multiline": True}, StringType.MLB),
        ({"literal": True, "multiline": True}, StringType.MLL),
    ],
)
def test_created_string_type(kwargs, expected):
    assert tomlkit.string("x", **kwargs).type is expected
