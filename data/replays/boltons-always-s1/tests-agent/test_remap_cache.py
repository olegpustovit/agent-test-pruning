from boltons.iterutils import remap, research


def _count_enters(cache):
    seen = []

    def enter(path, key, value):
        seen.append(path + (key,))
        return remap.__globals__['default_enter'](path, key, value)

    shared = ("hello",)
    remap({'a': shared, 'b': shared}, enter=enter, cache=cache)
    return seen


def test_cache_default_skips_shared_object_reenter():
    seen = _count_enters(True)
    assert ('b', 0) not in seen and ('a', 0) in seen


def test_cache_disabled_enters_every_occurrence():
    seen = _count_enters(False)
    assert ('a',) in seen and ('b',) in seen
    assert ('a', 0) in seen and ('b', 0) in seen


def test_cache_default_matches_explicit_true():
    root = {'a': [1, 2], 'b': (3,)}
    assert remap(root) == remap(root, cache=True) == root


def test_research_finds_shared_tuples():
    shared = ("hello",)
    root = {'a': shared, 'b': shared}
    res = research(root, query=lambda p, k, v: v == "hello")
    assert sorted(res) == [(('a', 0), 'hello'), (('b', 0), 'hello')]
