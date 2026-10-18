import sys

from boltons import tbutils
from boltons.tbutils import ParsedException

PLAIN_TB = '''Traceback (most recent call last):
  File "a.py", line 10, in <module>
    foo(1) + bar(2)
  File "b.py", line 3, in foo
    return 1 / 0
ZeroDivisionError: division by zero'''

ANCHOR_TB = '''Traceback (most recent call last):
  File "a.py", line 10, in <module>
    foo(1) + bar(2)
    ~~~~~~~^^^^^^^^
  File "b.py", line 3, in foo
    return 1 / 0
           ~~^~~
ZeroDivisionError: division by zero'''


def test_roundtrip_without_anchors():
    assert ParsedException.from_string(PLAIN_TB).to_string() == PLAIN_TB


def test_to_string_roundtrips_anchors():
    pe = ParsedException.from_string(ANCHOR_TB)
    assert [f.get('source_line_anchor') for f in pe.frames] == [
        '~~~~~~~^^^^^^^^', '       ~~^~~']
    assert pe.to_string() == ANCHOR_TB


def test_anchor_absent_for_plain_frames():
    pe = ParsedException.from_string(PLAIN_TB)
    assert all('source_line_anchor' not in f for f in pe.frames)


def test_anchor_dedented_with_deeper_indent():
    tb = (
        'Traceback (most recent call last):\n'
        '  File "a.py", line 1, in <module>\n'
        '        x + y\n'
        '        ~~^~~\n'
        'ValueError: hi'
    )
    pe = ParsedException.from_string(tb)
    assert pe.frames[0]['source_line_anchor'] == '~~^~~'
    assert pe.to_string().splitlines()[2:4] == ['    x + y', '    ~~^~~']


def test_docstring_documents_anchor_roundtrip():
    doc = ParsedException.to_string.__doc__
    assert 'source_line_anchor' in doc
    assert 'round-trip' in doc


def test_fix_print_exception_sets_hook():
    old = sys.excepthook
    try:
        tbutils.fix_print_exception()
        assert sys.excepthook is tbutils.print_exception
    finally:
        sys.excepthook = old
