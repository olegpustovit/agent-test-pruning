import threading

import pytest

from boltons.funcutils import once


def test_none_result_cached():
    calls = []

    @once
    def f():
        calls.append(1)
        return None

    assert f() is None
    assert f() is None
    assert len(calls) == 1


def test_exception_not_cached():
    calls = []

    @once
    def f():
        calls.append(1)
        if len(calls) == 1:
            raise ValueError('boom')
        return 'ok'

    with pytest.raises(ValueError):
        f()
    assert f() == 'ok'
    assert f() == 'ok'
    assert len(calls) == 2


def test_wraps_metadata_and_no_functools_cache():
    @once
    def f():
        "doc"
        return 1

    assert f.__name__ == 'f'
    assert f.__doc__ == 'doc'
    assert not hasattr(f, 'cache_info')


def test_independent_instances():
    def make(v):
        @once
        def f():
            return v
        return f

    assert make(1)() == 1
    assert make(2)() == 2


def test_threads_run_once():
    calls = []
    start = threading.Barrier(8)

    @once
    def f():
        calls.append(1)
        return object()

    results = []

    def run():
        start.wait()
        results.append(f())

    ts = [threading.Thread(target=run) for _ in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert len(calls) == 1
    assert len({id(r) for r in results}) == 1
