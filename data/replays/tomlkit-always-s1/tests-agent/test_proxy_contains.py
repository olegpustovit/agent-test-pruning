import pytest

import tomlkit

from tomlkit.container import OutOfOrderTableProxy
from tomlkit.items import SingleKey


TEXT = """\
[a.b]
x = 1
[c]
[a.d]
y = 2
"""


@pytest.fixture
def proxy():
    p = tomlkit.parse(TEXT)["a"]
    assert isinstance(p, OutOfOrderTableProxy)
    return p


def test_contains_defined_natively():
    assert "__contains__" in OutOfOrderTableProxy.__dict__


def test_present_and_absent(proxy):
    assert "b" in proxy
    assert "d" in proxy
    assert "x" not in proxy
    assert "missing" not in proxy
    assert SingleKey("b") in proxy
    assert SingleKey("zzz") not in proxy


def test_does_not_resolve_value(proxy, monkeypatch):
    def boom(self, key):
        raise AssertionError("__getitem__ must not be used")

    monkeypatch.setattr(OutOfOrderTableProxy, "__getitem__", boom)
    assert "b" in proxy
    assert "nope" not in proxy


@pytest.mark.parametrize("bad", [1, None, 1.5, (1,)])
def test_non_str_raises_type_error(proxy, bad):
    with pytest.raises(TypeError):
        bad in proxy


def test_no_mutation(proxy):
    doc = tomlkit.parse(TEXT)
    p = doc["a"]
    _ = "b" in p, "nope" in p
    assert doc.as_string() == TEXT


def test_after_modification(proxy):
    proxy["e"] = 3
    assert "e" in proxy
    del proxy["b"]
    assert "b" not in proxy
