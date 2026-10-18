from datetime import datetime
from datetime import time

import tomlkit



def test_datetime_unwrap_keeps_fold():
    item = tomlkit.item(datetime(2020, 1, 2, 3, 4, 5, 6, fold=1))
    assert item.fold == 1
    result = item.unwrap()
    assert type(result) is datetime
    assert result.fold == 1
    assert result == datetime(2020, 1, 2, 3, 4, 5, 6, fold=1)


def test_datetime_unwrap_default_fold():
    result = tomlkit.item(datetime(2020, 1, 2, 3, 4, 5)).unwrap()
    assert result.fold == 0


def test_time_unwrap_keeps_fold():
    item = tomlkit.item(time(3, 4, 5, 6, fold=1))
    assert item.fold == 1
    result = item.unwrap()
    assert type(result) is time
    assert result.fold == 1


def test_time_unwrap_default_fold():
    assert tomlkit.item(time(3, 4, 5)).unwrap().fold == 0


def test_document_unwrap_keeps_fold():
    doc = tomlkit.document()
    doc["d"] = datetime(2020, 1, 2, 3, 4, 5, fold=1)
    doc["t"] = time(3, 4, 5, fold=1)
    data = doc.unwrap()
    assert data["d"].fold == 1
    assert data["t"].fold == 1
