import io
import json

import pytest

from boltons.jsonutils import JSONLIterator

DATA = "".join(json.dumps({"id": i}) + "\n" for i in range(10))


def test_explicit_rel_seek_one_forward_is_empty():
    assert list(JSONLIterator(io.StringIO(DATA), rel_seek=1.0)) == []


def test_explicit_rel_seek_one_reverse_yields_all_reversed():
    out = list(JSONLIterator(io.BytesIO(DATA.encode()), reverse=True, rel_seek=1.0))
    assert [o["id"] for o in out] == list(range(9, -1, -1))


def test_rel_seek_one_matches_default_reverse():
    a = list(JSONLIterator(io.BytesIO(DATA.encode()), reverse=True))
    b = list(JSONLIterator(io.BytesIO(DATA.encode()), reverse=True, rel_seek=1))
    assert a == b


@pytest.mark.parametrize("bad", [-1.0, 1.01, 2, -1.5])
def test_rel_seek_out_of_range_still_rejected(bad):
    with pytest.raises(ValueError):
        JSONLIterator(io.StringIO(DATA), rel_seek=bad)
