import collections.abc as cabc
import math

import tomlkit

from tomlkit import _utils
from tomlkit import api
from tomlkit import container
from tomlkit import exceptions
from tomlkit import items


def test_abc_types_come_from_collections_abc():
    assert _utils.Collection is cabc.Collection
    assert exceptions.Collection is cabc.Collection
    assert api.Iterable is cabc.Iterable
    assert container.Iterator is cabc.Iterator
    assert items.Collection is cabc.Collection
    assert items.Iterable is cabc.Iterable
    assert items.Iterator is cabc.Iterator
    assert items.Sequence is cabc.Sequence


def test_float_ceil_floor():
    doc = tomlkit.parse("a = 1.5\nb = -1.5\n")
    assert math.ceil(doc["a"]) == 2
    assert math.floor(doc["a"]) == 1
    assert math.ceil(doc["b"]) == -1
    assert math.floor(doc["b"]) == -2
    assert items.Float.__ceil__ is float.__ceil__
    assert items.Float.__floor__ is float.__floor__


def test_roundtrip_still_works():
    text = "[a]\nx = [1, 2]\n"
    assert tomlkit.dumps(tomlkit.parse(text)) == text
    assert list(iter(tomlkit.parse(text)["a"])) == ["x"]
