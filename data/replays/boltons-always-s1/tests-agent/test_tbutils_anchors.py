from boltons.tbutils import ParsedException

ANCHOR_TB = '''Traceback (most recent call last):
  File "a.py", line 10, in <module>
    foo(1) + bar(2)
    ~~~~~~~^^^^^^^^
  File "b.py", line 3, in foo
    return 1 / 0
           ~~^~~
ZeroDivisionError: division by zero
'''


def test_anchor_lines_skipped():
    pe = ParsedException.from_string(ANCHOR_TB)
    assert pe.exc_type == 'ZeroDivisionError'
    assert pe.exc_msg == 'division by zero'
    assert [f['source_line'] for f in pe.frames] == ['foo(1) + bar(2)', 'return 1 / 0']
    assert [f['funcname'] for f in pe.frames] == ['<module>', 'foo']
    assert [f['lineno'] for f in pe.frames] == ['10', '3']


def test_no_anchor_still_works():
    tb = '''Traceback (most recent call last):
  File "a.py", line 1, in <module>
    x()
  File "b.py", line 2, in x
    raise ValueError("hi")
ValueError: hi
'''
    pe = ParsedException.from_string(tb)
    assert len(pe.frames) == 2
    assert pe.exc_type == 'ValueError'
    assert pe.exc_msg == 'hi'
