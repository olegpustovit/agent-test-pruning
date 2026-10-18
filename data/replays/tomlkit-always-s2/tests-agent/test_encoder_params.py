import pytest

import tomlkit

from tomlkit.exceptions import ConvertError


class Custom:
    def __init__(self, data):
        self.data = data


@pytest.fixture
def register():
    added = []

    def _reg(enc):
        tomlkit.register_encoder(enc)
        added.append(enc)
        return enc

    yield _reg
    for enc in added:
        tomlkit.unregister_encoder(enc)


def test_new_style_encoder_receives_parent_and_sort_keys(register):
    seen = {}

    def enc(obj, _parent=None, _sort_keys=False):
        if not isinstance(obj, Custom):
            raise ConvertError("no")
        seen["parent"] = _parent
        seen["sort"] = _sort_keys
        tbl = tomlkit.table()
        for k, v in obj.data.items():
            tbl[k] = tomlkit.item(v, _parent=tbl, _sort_keys=_sort_keys)
        return tbl

    register(enc)
    doc = tomlkit.item({"x": Custom({"b": 1, "a": {"d": 1, "c": 2}})}, _sort_keys=True)
    assert seen["sort"] is True
    assert doc["x"]["a"]["c"] == 2
    assert list(doc["x"]["a"].keys()) == ["c", "d"]

    tomlkit.item(Custom({}))
    assert seen["sort"] is False
    assert seen["parent"] is None


def test_kwargs_encoder(register):
    got = {}

    def enc(obj, **kwargs):
        if not isinstance(obj, Custom):
            raise ConvertError("no")
        got.update(kwargs)
        return tomlkit.item(1)

    register(enc)
    tomlkit.item(Custom({}), _sort_keys=True)
    assert got == {"_parent": None, "_sort_keys": True}


def test_old_style_encoder_still_works(register):
    def enc(obj):
        if not isinstance(obj, Custom):
            raise ConvertError("no")
        return tomlkit.item(42)

    register(enc)
    assert tomlkit.dumps({"a": Custom({})}) == "a = 42\n"
    assert tomlkit.item(Custom({}), _sort_keys=True) == 42
