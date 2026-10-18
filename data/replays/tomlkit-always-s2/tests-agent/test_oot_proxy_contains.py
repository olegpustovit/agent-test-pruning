import tomlkit

from tomlkit.container import OutOfOrderTableProxy


DOC = """\
[tool.a]
x = 1

[other]
y = 2

[tool.b]
z = 3
"""


def _proxy():
    doc = tomlkit.parse(DOC)
    tool = doc["tool"]
    assert isinstance(tool, OutOfOrderTableProxy)
    return doc, tool


def test_contains_present_and_absent():
    _, tool = _proxy()
    assert "a" in tool
    assert "b" in tool
    assert "missing" not in tool
    assert "x" not in tool  # nested key, not a direct one


def test_contains_does_not_use_getitem(monkeypatch):
    _, tool = _proxy()

    def boom(self, key):
        raise AssertionError("__getitem__ called")

    monkeypatch.setattr(OutOfOrderTableProxy, "__getitem__", boom)
    assert "a" in tool
    assert "nope" not in tool


def test_contains_returns_bool_and_no_mutation():
    doc, tool = _proxy()
    before = doc.as_string()
    assert ("a" in tool) is True
    assert ("zzz" in tool) is False
    assert doc.as_string() == before == DOC


def test_contains_matches_keys():
    _, tool = _proxy()
    for k in list(tool.keys()) + ["q", "other"]:
        assert (k in tool) == (k in set(tool.keys()))


def test_contains_after_delete():
    _, tool = _proxy()
    del tool["a"]
    assert "a" not in tool
    assert "b" in tool
