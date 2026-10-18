import tomlkit


DOC = """\
[a.b.c]
x = 1
[x]
y = 2
[a.b.d]
z = 3
"""


def test_access_out_of_order_table_reads_values():
    doc = tomlkit.parse(DOC)
    assert doc["a"]["b"]["c"]["x"] == 1
    assert doc["a"]["b"]["d"]["z"] == 3
    assert doc["x"]["y"] == 2


def test_unaccessed_document_roundtrips():
    doc = tomlkit.parse(DOC)
    assert doc.as_string() == DOC


def test_parsing_flag_unchanged_after_proxy_construction():
    doc = tomlkit.parse(DOC)
    before = doc._parsed
    doc["a"]
    assert doc._parsed == before


def test_modify_through_proxy_updates_value():
    doc = tomlkit.parse(DOC)
    doc["a"]["b"]["d"]["z"] = 5
    reparsed = tomlkit.parse(doc.as_string())
    assert reparsed["a"]["b"]["d"]["z"] == 5
    assert reparsed["a"]["b"]["c"]["x"] == 1
    assert reparsed["x"]["y"] == 2
