import tomlkit

DOC = """[a.b]
x = 1

[c]
y = 2

[a.d]
z = 3
"""


def _proxy():
    p = tomlkit.parse(DOC)["a"]
    assert type(p).__name__ == "OutOfOrderTableProxy"
    return p


def test_repr_is_merged_value():
    p = _proxy()
    assert repr(p) == repr(p.value)
    assert repr(p) == repr({"b": {"x": 1}, "d": {"z": 3}})


def test_str_is_merged_value():
    p = _proxy()
    assert str(p) == str(p.value)
    assert "OutOfOrderTableProxy" not in str(p)
    assert "'d'" in str(p) and "'z': 3" in str(p)
