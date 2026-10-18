from tomlkit import dumps, parse


def test_dumps_sort_keys_parsed_document():
    doc = parse("b = 1\na = 2\n\n[t]\nz = 1\ny = 2\n")
    out = dumps(doc, sort_keys=True)
    assert out.index("a = 2") < out.index("b = 1")
    assert parse(out) == doc


def test_dumps_parsed_document_unsorted_preserves_order():
    src = "b = 1\na = 2\n"
    assert dumps(parse(src)) == src
    assert dumps(parse(src), sort_keys=False) == src


def test_dumps_sort_keys_does_not_mutate_document():
    src = "b = 1\na = 2\n"
    doc = parse(src)
    dumps(doc, sort_keys=True)
    assert doc.as_string() == src
