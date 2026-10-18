import pytest

from tomlkit import parse, string
from tomlkit.items import StringType


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, StringType.SLB),
        ({"literal": True}, StringType.SLL),
        ({"multiline": True}, StringType.MLB),
        ({"literal": True, "multiline": True}, StringType.MLL),
    ],
)
def test_string_type_from_factory(kwargs, expected):
    assert string("abc", **kwargs).type is expected


def test_string_type_from_parsed_document():
    doc = parse("a = 'x'\nb = \"y\"\nc = '''z'''\nd = \"\"\"w\"\"\"\n")
    assert doc["a"].type is StringType.SLL
    assert doc["b"].type is StringType.SLB
    assert doc["c"].type is StringType.MLL
    assert doc["d"].type is StringType.MLB
