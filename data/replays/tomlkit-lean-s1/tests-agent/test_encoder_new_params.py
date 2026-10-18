import pytest

from tomlkit import api
from tomlkit.exceptions import ConvertError


class Custom:
    def __init__(self, d):
        self.d = d


def _run(enc, value):
    api.register_encoder(enc)
    try:
        return api.item(value)
    finally:
        api.unregister_encoder(enc)


def test_encoder_receives_parent_and_sort_keys():
    seen = {}

    def enc(obj, _parent=None, _sort_keys=False):
        if not isinstance(obj, Custom):
            raise ConvertError("no")
        seen["parent"] = _parent
        seen["sort"] = _sort_keys
        return api.item(obj.d, _parent=_parent, _sort_keys=_sort_keys)

    api.register_encoder(enc)
    try:
        api.item(Custom({"b": 1, "a": 2}), _sort_keys=True)
    finally:
        api.unregister_encoder(enc)
    assert seen == {"parent": None, "sort": True}


def test_encoder_with_var_kwargs():
    seen = {}

    def enc(obj, **kwargs):
        if not isinstance(obj, Custom):
            raise ConvertError("no")
        seen.update(kwargs)
        return api.item(obj.d)

    _run(enc, Custom({"a": 1}))
    assert seen == {"_parent": None, "_sort_keys": False}


def test_old_style_encoder_still_works():
    def enc(obj):
        if not isinstance(obj, Custom):
            raise ConvertError("no")
        return api.item(obj.d)

    assert _run(enc, Custom({"a": 1})) == {"a": 1}


def test_nested_custom_with_sort_keys():
    def enc(obj, _parent=None, _sort_keys=False):
        if not isinstance(obj, Custom):
            raise ConvertError("no")
        tbl = api.table()
        for k, v in obj.d.items():
            tbl[k] = api.item(v, _parent=tbl, _sort_keys=_sort_keys)
        return tbl

    api.register_encoder(enc)
    try:
        doc = api.document()
        doc["x"] = api.item({"o": Custom({"b": 1, "a": 2})}, _sort_keys=True)
    finally:
        api.unregister_encoder(enc)
    assert doc["x"]["o"] == {"a": 2, "b": 1}
