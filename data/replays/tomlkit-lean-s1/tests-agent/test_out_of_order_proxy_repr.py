import tomlkit

from tomlkit.container import OutOfOrderTableProxy


DOC = "[a.b]\nx = 1\n[c]\ny = 1\n[a.d]\nz = 1\n"


def test_proxy_repr_and_str_show_merged_values():
    doc = tomlkit.parse(DOC)
    proxy = doc["a"]
    assert isinstance(proxy, OutOfOrderTableProxy)
    expected = "{'b': {'x': 1}, 'd': {'z': 1}}"
    assert repr(proxy) == expected
    assert str(proxy) == expected
    assert doc.as_string() == DOC
