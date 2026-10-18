import pytest

import tomlkit

from tomlkit.exceptions import ConvertError
from tomlkit.exceptions import TOMLKitError
from tomlkit.items import Item


def test_convert_error_hierarchy():
    assert issubclass(ConvertError, TypeError)
    assert issubclass(ConvertError, ValueError)
    assert issubclass(ConvertError, TOMLKitError)


def test_unsupported_type_raises_convert_error():
    with pytest.raises(ConvertError, match="Unable to convert an object of"):
        tomlkit.item(object())


def test_encoder_convert_error_falls_through():
    def enc(v):
        raise ConvertError("nope")

    tomlkit.register_encoder(enc)
    try:
        with pytest.raises(ConvertError):
            tomlkit.item(object())
    finally:
        tomlkit.unregister_encoder(enc)


def test_encoder_external_type_error_propagates():
    def enc(v):
        raise TypeError("external")

    tomlkit.register_encoder(enc)
    try:
        with pytest.raises(TypeError, match="external") as ei:
            tomlkit.item(object())
        assert not isinstance(ei.value, ConvertError)
    finally:
        tomlkit.unregister_encoder(enc)


def test_encoder_bad_return_type():
    def enc(v):
        return 1

    tomlkit.register_encoder(enc)
    try:
        with pytest.raises(ConvertError, match="expected to return an instance of Item"):
            tomlkit.item(object())
    finally:
        tomlkit.unregister_encoder(enc)


def test_encoder_success():
    class Foo:
        pass

    def enc(v):
        if isinstance(v, Foo):
            return tomlkit.item(42)
        raise ConvertError("no")

    tomlkit.register_encoder(enc)
    try:
        assert isinstance(tomlkit.item(Foo()), Item)
        assert tomlkit.item(Foo()) == 42
    finally:
        tomlkit.unregister_encoder(enc)
