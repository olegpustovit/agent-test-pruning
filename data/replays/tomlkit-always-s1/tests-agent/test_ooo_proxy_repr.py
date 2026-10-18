import tomlkit

from tomlkit.container import OutOfOrderTableProxy


DOC = """[a.b]
x = 1

[c]
y = 2

[a.d]
z = 3
"""


def test_proxy_str_and_repr_show_merged_value():
    doc = tomlkit.parse(DOC)
    proxy = doc["a"]
    assert isinstance(proxy, OutOfOrderTableProxy)
    expected = {"b": {"x": 1}, "d": {"z": 3}}
    assert str(proxy) == str(proxy.value)
    assert repr(proxy) == repr(proxy.value)
    assert "b" in str(proxy) and "d" in str(proxy)
    assert "'z': 3" in repr(proxy)
    assert proxy == expected
