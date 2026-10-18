import io
import json

import pytest

from boltons.jsonutils import JSONLIterator

LINES = [{"id": i, "pad": "x" * 30} for i in range(200)]
DATA = "".join(json.dumps(o) + "\n" for o in LINES)


def _txt():
    return io.StringIO(DATA)


@pytest.mark.parametrize("rel", [0.25, 0.5, 0.75, -0.3])
def test_text_rel_seek_starts_on_line_boundary(rel):
    out = list(JSONLIterator(_txt(), rel_seek=rel))
    ids = [o["id"] for o in out]
    assert ids and ids[0] > 0
    assert ids == list(range(ids[0], 200))


def test_text_no_trailing_newline_after_seek():
    f = io.StringIO('{"a": 1}\n{"a": 2}\n{"a": 3}')
    assert list(JSONLIterator(f, rel_seek=0.9)) == []
