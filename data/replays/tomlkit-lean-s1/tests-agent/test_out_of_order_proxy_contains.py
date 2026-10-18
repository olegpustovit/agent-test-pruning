import tomlkit

from tomlkit.container import OutOfOrderTableProxy
from tomlkit.items import SingleKey


DOC = "[a.b]\nx = 1\n[c]\ny = 1\n[a.d]\nz = 1\n"


def test_proxy_contains_no_mutation_and_no_raise():
    doc = tomlkit.parse(DOC)
    proxy = doc["a"]
    assert isinstance(proxy, OutOfOrderTableProxy)
    assert "b" in proxy
    assert "d" in proxy
    assert "zzz" not in proxy
    assert SingleKey("b") in proxy
    assert doc.as_string() == DOC


def test_proxy_contains_matches_getitem():
    proxy = tomlkit.parse(DOC)["a"]
    for k in ("b", "d", "missing"):
        try:
            proxy[k]
            expected = True
        except KeyError:
            expected = False
        assert (k in proxy) is expected
