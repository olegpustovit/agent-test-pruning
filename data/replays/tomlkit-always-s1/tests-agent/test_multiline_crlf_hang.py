import multiprocessing

import pytest

import tomlkit

from tomlkit.exceptions import UnexpectedEofError


def _parse(src, q):
    try:
        q.put(("ok", tomlkit.parse(src).unwrap()))
    except Exception as e:  # noqa: BLE001
        q.put(("err", type(e)))


def _run(src, timeout=10):
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=_parse, args=(src, q))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        pytest.fail("parser hung")
    return q.get(timeout=5)


@pytest.mark.parametrize("q", ['"""', "'''"])
def test_crlf_in_multiline_string(q):
    src = f"a = {q}x\r\ny\r\nz{q}\r\n"
    assert _run(src) == ("ok", {"a": "x\r\ny\r\nz"})


def test_crlf_value_preserved():
    doc = tomlkit.parse('a = """x\r\ny"""\r\n')
    assert doc["a"] == "x\r\ny"
    assert doc.as_string() == 'a = """x\r\ny"""\r\n'


def test_crlf_unterminated_raises_eof():
    kind, res = _run('a = """x\r\n')
    assert kind == "err"
    assert issubclass(res, UnexpectedEofError)


def test_crlf_at_start_of_multiline():
    assert _run('a = """\r\n\r\nx"""')[0] == "ok"
