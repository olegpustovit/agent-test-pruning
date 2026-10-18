import pytest

from tomlkit import dumps
from tomlkit import loads


DOC = "a = [\n  1\n  # c\n  , 2\n]\n"


@pytest.mark.parametrize("method", ["append", "insert_end"])
def test_comma_first_insert_reparses(method):
    doc = loads(DOC)
    arr = doc["a"]
    if method == "append":
        arr.append(99)
        expected = [1, 2, 99]
    else:
        arr.insert(2, 99)
        expected = [1, 2, 99]
    out = dumps(doc)
    assert ",," not in out.replace(" ", "").replace("\n", "")
    assert loads(out)["a"] == expected
