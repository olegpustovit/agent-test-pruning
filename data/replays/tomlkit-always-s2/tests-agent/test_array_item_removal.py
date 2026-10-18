import pytest

from tomlkit import dumps
from tomlkit import parse


@pytest.mark.parametrize(
    "src, idx, expected",
    [
        ("a = [1, 2, 3]\n", 0, "a = [2, 3]\n"),
        ("a = [1, 2, 3]\n", 1, "a = [1, 3]\n"),
        ("a = [1, 2, 3]\n", 2, "a = [1, 2]\n"),
        ("a = [\n  1,\n  2,\n  3,\n]\n", 0, "a = [\n  2,\n  3,\n]\n"),
        ("a = [\n  1,\n  2,\n  3,\n]\n", 1, "a = [\n  1,\n  3,\n]\n"),
        ("a = [\n  1,\n  2,\n  3,\n]\n", 2, "a = [\n  1,\n  2,\n]\n"),
        ("a = [\n  1,\n  2,\n]\n", 0, "a = [\n  2,\n]\n"),
        ("a = [\n  1, # c\n  2,\n]\n", 1, "a = [\n  1, # c\n]\n"),
    ],
)
def test_remove_item_preserves_format(src, idx, expected):
    doc = parse(src)
    del doc["a"][idx]
    assert doc.as_string() == expected
    # result must remain valid TOML
    assert parse(doc.as_string())["a"] == list(doc["a"])


def test_parser_roundtrip_with_spaced_commas():
    src = "a = [1 , 2 ,\n  3 ,\n]\n"
    assert dumps(parse(src)) == src
