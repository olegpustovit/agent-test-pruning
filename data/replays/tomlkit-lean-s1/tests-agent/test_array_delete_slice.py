import pytest

from tomlkit import dumps
from tomlkit import parse


@pytest.mark.parametrize(
    "sl",
    [slice(1, None), slice(None, 2), slice(None, None, 2), slice(-2, None), slice(None, -1), slice(None, None, -1)],
)
def test_delete_slice_matches_list(sl):
    doc = parse("a = [1, 2, 3, 4, 5]")
    expected = [1, 2, 3, 4, 5]
    del doc["a"][sl]
    del expected[sl]
    assert doc["a"] == expected
    assert parse(dumps(doc))["a"] == expected
