import pytest

import tomlkit

from tomlkit import api
from tomlkit.exceptions import ConvertError
from tomlkit.items import item


def test_register_encoder_doc_mentions_convert_error():
    doc = api.register_encoder.__doc__
    assert "ConvertError" in doc
    assert "TypeError" not in doc


def test_custom_encoder_raising_convert_error_is_handled():
    class Foo:
        pass

    class Bar:
        pass

    @tomlkit.register_encoder
    def enc(obj, _parent=None, _sort_keys=False):
        if isinstance(obj, Foo):
            return item(1)
        raise ConvertError("nope")

    try:
        assert item(Foo()) == 1
        with pytest.raises(ConvertError):
            item(Bar())
    finally:
        tomlkit.unregister_encoder(enc)
