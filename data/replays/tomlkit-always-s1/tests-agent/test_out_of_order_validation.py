import pytest

import tomlkit

from tomlkit.container import OutOfOrderTableProxy
from tomlkit.exceptions import TOMLKitError


OUT_OF_ORDER = """\
[a.b]
x = 1
[c]
[a.d]
y = 2
"""


def test_out_of_order_roundtrip():
    doc = tomlkit.parse(OUT_OF_ORDER)
    assert doc.as_string() == OUT_OF_ORDER
    assert doc.unwrap() == {"a": {"b": {"x": 1}, "d": {"y": 2}}, "c": {}}
    assert doc["a"]["d"]["y"] == 2


def test_nested_out_of_order_roundtrip():
    text = "[a.b.c]\nx=1\n[z]\n[a.b.c.d]\ny=2\n[a.b.e]\n"
    doc = tomlkit.parse(text)
    assert doc.as_string() == text
    assert doc.unwrap() == {"a": {"b": {"c": {"x": 1, "d": {"y": 2}}, "e": {}}}, "z": {}}


@pytest.mark.parametrize(
    "text",
    [
        "[a.b]\nx=1\n[c]\n[a.b]\ny=2\n",
        "[a.b]\nx=1\n[c]\n[a.b]\nx=2\n",
        "[a]\nx=1\n[c]\n[a]\ny=1\n",
    ],
)
def test_duplicate_tables_still_rejected(text):
    with pytest.raises(TOMLKitError):
        tomlkit.parse(text)


def test_redefinition_in_out_of_order_table_rejected():
    with pytest.raises(TOMLKitError):
        tomlkit.parse("[a]\nb.x=1\n[a.b]\ny=2\n").unwrap()


def test_proxy_construction_does_not_scale_with_table_count(monkeypatch):
    count = 0
    orig = OutOfOrderTableProxy.__init__

    def counting(self, *args, **kwargs):
        nonlocal count
        count += 1
        orig(self, *args, **kwargs)

    monkeypatch.setattr(OutOfOrderTableProxy, "__init__", counting)
    n = 10
    text = "[a.b]\nx=1\n" + "".join(f"[c{i}]\n" for i in range(n)) + "[a.d]\ny=1\n"
    tomlkit.parse(text)
    assert count < 5 * n


def test_table_add_out_of_order_still_works():
    doc = tomlkit.parse(OUT_OF_ORDER)
    doc["a"]["e"] = 3
    assert doc["a"]["e"] == 3
    assert "e = 3" in doc.as_string()
