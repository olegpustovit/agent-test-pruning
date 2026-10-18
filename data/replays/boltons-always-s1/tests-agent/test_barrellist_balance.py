from boltons.listutils import BarrelList


def test_balance_splits_oversized_list():
    bl = BarrelList()
    bl.lists[0].extend(range(30000))
    assert bl._balance_list(0) is True
    assert len(bl.lists) > 1
    assert [x for l in bl.lists for x in l] == list(range(30000))


def test_balance_small_list_noop():
    bl = BarrelList([1, 2, 3])
    assert bl._balance_list(0) is False
    assert bl.lists == [[1, 2, 3]]


def test_balance_negative_index():
    bl = BarrelList()
    bl.lists[0].extend(range(30000))
    assert bl._balance_list(-1) is True
    assert [x for l in bl.lists for x in l] == list(range(30000))


def test_balance_does_not_call_len_extra(monkeypatch):
    calls = []
    orig = BarrelList.__len__

    def counting(self):
        calls.append(1)
        return orig(self)

    bl = BarrelList([1, 2, 3])
    monkeypatch.setattr(BarrelList, '__len__', counting)
    bl._balance_list(0)
    # only _cur_size_limit should call len(self)
    assert len(calls) == 1


def test_insert_keeps_order():
    bl = BarrelList()
    for i in range(200):
        bl.insert(0, i)
    assert list(bl) == list(range(199, -1, -1))
