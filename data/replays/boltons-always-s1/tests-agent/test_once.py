import threading

from boltons.funcutils import once


def test_runs_once_and_caches():
    calls = []

    @once
    def f():
        calls.append(1)
        return 'x'

    assert f() == 'x'
    assert f() == 'x'
    assert len(calls) == 1


def test_none_result_cached():
    calls = []

    @once
    def f():
        calls.append(1)

    assert f() is None
    assert f() is None
    assert len(calls) == 1


def test_independent_per_function():
    @once
    def a():
        return 'a'

    @once
    def b():
        return 'b'

    assert a() == 'a'
    assert b() == 'b'
    assert a() == 'a'


def test_wraps_metadata():
    @once
    def f():
        """doc"""

    assert f.__name__ == 'f'
    assert f.__doc__ == 'doc'


def test_thread_safe():
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
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert len(calls) == 1
    assert len({id(r) for r in results}) == 1


def test_docstring_mentions_logging():
    assert 'logging' in once.__doc__
