import pytest

from tomlkit import api
from tomlkit.exceptions import ConvertError
from tomlkit.exceptions import TOMLKitError


def test_convert_error_hierarchy():
    assert issubclass(ConvertError, TypeError)
    assert issubclass(ConvertError, ValueError)
    assert issubclass(ConvertError, TOMLKitError)


def test_unsupported_type_raises_convert_error():
    with pytest.raises(ConvertError):
        api.item(object())


def test_encoder_raising_convert_error_falls_through():
    def enc(obj):
        raise ConvertError("nope")

    api.register_encoder(enc)
    try:
        with pytest.raises(ConvertError):
            api.item(object())
    finally:
        api.unregister_encoder(enc)


def test_external_type_error_in_encoder_propagates():
    def enc(obj):
        raise TypeError("internal bug")

    api.register_encoder(enc)
    try:
        with pytest.raises(TypeError, match="internal bug") as exc:
            api.item(object())
        assert not isinstance(exc.value, ConvertError)
    finally:
        api.unregister_encoder(enc)


def test_encoder_returning_non_item_raises_convert_error():
    def enc(obj):
        return 1

    api.register_encoder(enc)
    try:
        with pytest.raises(ConvertError, match="Item"):
            api.item(object())
    finally:
        api.unregister_encoder(enc)
