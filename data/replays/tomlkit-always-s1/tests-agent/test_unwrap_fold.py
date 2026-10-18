from datetime import datetime
from datetime import time

import tomlkit

from tomlkit.items import DateTime
from tomlkit.items import Time


def test_datetime_unwrap_keeps_fold():
    item = tomlkit.item(datetime(2020, 1, 1, 1, 30, fold=1))
    assert isinstance(item, DateTime)
    assert item.fold == 1
    result = item.unwrap()
    assert type(result) is datetime
    assert result.fold == 1


def test_datetime_unwrap_fold_default_zero():
    result = tomlkit.item(datetime(2020, 1, 1, 1, 30)).unwrap()
    assert result.fold == 0


def test_time_unwrap_keeps_fold():
    item = tomlkit.item(time(1, 30, fold=1))
    assert isinstance(item, Time)
    result = item.unwrap()
    assert type(result) is time
    assert result.fold == 1


def test_time_unwrap_fold_default_zero():
    assert tomlkit.item(time(1, 30)).unwrap().fold == 0


def test_document_unwrap_keeps_fold():
    doc = tomlkit.document()
    doc["d"] = datetime(2020, 1, 1, 1, 30, fold=1)
    doc["t"] = time(1, 30, fold=1)
    out = doc.unwrap()
    assert out["d"].fold == 1
    assert out["t"].fold == 1
