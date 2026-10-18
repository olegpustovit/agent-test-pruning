from tomlkit.toml_file import TOMLFile


def test_read_crlf_normalizes_document_newlines(tmp_path):
    path = tmp_path / "a.toml"
    path.write_bytes(b'a = 1\r\n[t]\r\nb = """x\r\ny"""\r\n')
    doc = TOMLFile(path).read()

    assert "\r" not in doc.as_string()
    assert doc["t"]["b"] == "x\ny"


def test_crlf_roundtrip_with_added_item_is_consistent(tmp_path):
    path = tmp_path / "a.toml"
    path.write_bytes(b"a = 1\r\n[t]\r\nb = 2\r\n")
    f = TOMLFile(path)
    doc = f.read()
    doc["t"]["c"] = 3
    f.write(doc)

    data = path.read_bytes()
    assert data == b"a = 1\r\n[t]\r\nb = 2\r\nc = 3\r\n"
    assert data.count(b"\n") == data.count(b"\r\n")
