from tomlkit.toml_file import TOMLFile


def _write(path, data: bytes):
    path.write_bytes(data)


def test_crlf_read_has_no_carriage_returns(tmp_path):
    p = tmp_path / "a.toml"
    _write(p, b'a = """x\r\ny"""\r\nb = 1\r\n')
    doc = TOMLFile(p).read()
    assert doc["a"] == "x\ny"
    assert "\r" not in doc.as_string()


def test_crlf_roundtrip_preserved(tmp_path):
    p = tmp_path / "a.toml"
    raw = b'a = """x\r\ny"""\r\nb = 1\r\n'
    _write(p, raw)
    f = TOMLFile(p)
    doc = f.read()
    doc["c"] = 2
    f.write(doc)
    out = p.read_bytes()
    assert out.count(b"\n") == out.count(b"\r\n")
    assert b"c = 2" in out


def test_lf_roundtrip(tmp_path):
    p = tmp_path / "a.toml"
    _write(p, b"a = 1\nb = 2\n")
    f = TOMLFile(p)
    f.write(f.read())
    assert p.read_bytes() == b"a = 1\nb = 2\n"


def test_mixed_endings_keep_content(tmp_path):
    p = tmp_path / "a.toml"
    raw = b"a = 1\r\nb = 2\n"
    _write(p, raw)
    f = TOMLFile(p)
    f.write(f.read())
    assert p.read_bytes() == raw
