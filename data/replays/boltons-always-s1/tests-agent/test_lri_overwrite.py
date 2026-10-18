from boltons.cacheutils import LRI, LRU


def test_lri_overwrite_updates_value():
    cache = LRI(max_size=3)
    cache['a'] = 1
    cache['b'] = 2
    cache['a'] = 10
    assert cache['a'] == 10
    assert dict.__getitem__(cache, 'a') == 10
    assert dict.__getitem__(cache, 'b') == 2
    assert len(cache) == 2


def test_lri_overwrite_when_full():
    cache = LRI(max_size=2)
    cache['a'] = 1
    cache['b'] = 2
    cache['a'] = 3
    assert dict(cache) == {'a': 3, 'b': 2}
    assert cache['a'] == 3
    assert list(cache.items()) == [(k, cache[k]) for k in cache]
    cache['c'] = 4
    assert len(cache) == 2
    assert 'c' in cache


def test_lru_overwrite_consistent():
    cache = LRU(max_size=2)
    cache['a'] = 1
    cache['a'] = 2
    assert dict.__getitem__(cache, 'a') == 2
    assert cache['a'] == 2
