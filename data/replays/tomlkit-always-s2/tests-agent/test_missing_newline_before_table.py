import tomlkit


def _roundtrips(text):
    out = tomlkit.dumps(tomlkit.parse(text))
    assert out == text
    assert tomlkit.parse(out) == tomlkit.parse(text)


def test_table_after_aot_without_trailing_newline():
    doc = tomlkit.parse("[[a]]\nx=1")
    doc.add("b", tomlkit.table())
    doc["b"]["y"] = 2
    out = tomlkit.dumps(doc)
    assert out == "[[a]]\nx=1\n[b]\ny = 2\n"
    assert tomlkit.parse(out) == {"a": [{"x": 1}], "b": {"y": 2}}


def test_aot_after_table_without_trailing_newline():
    doc = tomlkit.parse("[t]\nx=1")
    doc["u"] = tomlkit.aot()
    doc["u"].append({"z": 1})
    out = tomlkit.dumps(doc)
    assert out == "[t]\nx=1\n[[u]]\nz = 1\n"
    assert tomlkit.parse(out) == {"t": {"x": 1}, "u": [{"z": 1}]}


def test_nested_table_after_aot_without_trailing_newline():
    doc = tomlkit.parse("[t]\n[[t.a]]\nx=1")
    doc["t"]["s"] = {"q": 1}
    out = tomlkit.dumps(doc)
    assert out == "[t]\n[[t.a]]\nx=1\n[t.s]\nq = 1\n"
    assert tomlkit.parse(out) == {"t": {"a": [{"x": 1}], "s": {"q": 1}}}


def test_existing_documents_unchanged():
    _roundtrips("[[a]]\nx=1\n\n[[b]]\ny=2")
    _roundtrips("a=1\n[t]\nx=1")
    _roundtrips("[a]\nx=1\n[[a.b]]\ny=1")
    _roundtrips("[[a]]\nx=1\n")
