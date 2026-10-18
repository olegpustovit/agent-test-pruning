import pytest

from boltons.urlutils import parse_qsl


def test_default_is_utf8():
    assert parse_qsl('k=%C3%A9') == [('k', '\xe9')]


def test_value_uses_encoding():
    assert parse_qsl('k=%E9', encoding='latin-1') == [('k', '\xe9')]


def test_key_uses_encoding():
    assert parse_qsl('%E9=v', encoding='latin-1') == [('\xe9', 'v')]


def test_plus_still_space_with_encoding():
    assert parse_qsl('a+b=c+d', encoding='latin-1') == [('a b', 'c d')]


def test_encoding_differs_from_utf8():
    # %E9 is invalid utf-8 (replaced), but valid latin-1
    assert parse_qsl('k=%E9')[0][1] != '\xe9'


def test_blank_value_with_encoding():
    assert parse_qsl('k', encoding='latin-1') == [('k', None)]
