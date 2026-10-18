from tomlkit import dumps
from tomlkit import loads
from tomlkit import parse


def test_dotted_table_header_roundtrip_preserves_display_name():
    doc = 'a = 1\n[x.y."z w"]\nk = 1\n\n[x.q]\nm = 2\n'
    parsed = parse(doc)
    assert dumps(parsed) == doc
    assert parsed["x"]["y"]["z w"]["k"] == 1
    assert parsed["x"]["q"]["m"] == 2


def test_aot_dotted_header_roundtrip():
    doc = "[[a.b]]\nx = 1\n\n[[a.b]]\nx = 2\n"
    parsed = parse(doc)
    assert dumps(parsed) == doc
    assert [t["x"] for t in parsed["a"]["b"]] == [1, 2]


def test_out_of_order_table_merge():
    doc = "[a.b]\nx = 1\n\n[c]\ny = 2\n\n[a.d]\nz = 3\n"
    parsed = loads(doc)
    assert parsed["a"]["b"]["x"] == 1
    assert parsed["a"]["d"]["z"] == 3
    assert dumps(parsed) == doc
    assert parsed.unwrap() == {"a": {"b": {"x": 1}, "d": {"z": 3}}, "c": {"y": 2}}
