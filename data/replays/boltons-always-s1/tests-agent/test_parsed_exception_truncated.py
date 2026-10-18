from boltons.tbutils import ParsedException


def test_truncated_after_source_line():
    tb = (
        'Traceback (most recent call last):\n'
        '  File "a.py", line 1, in f\n'
        '    do()'
    )
    pe = ParsedException.from_string(tb)
    assert len(pe.frames) == 1
    assert pe.frames[0]['source_line'] == 'do()'


def test_truncated_after_frame_line():
    tb = (
        'Traceback (most recent call last):\n'
        '  File "a.py", line 1, in f'
    )
    pe = ParsedException.from_string(tb)
    assert len(pe.frames) == 1
    assert pe.frames[0]['source_line'] == ''


def test_header_only():
    pe = ParsedException.from_string('Traceback (most recent call last):')
    assert pe.frames == []


def test_underline_anchor_still_skipped():
    tb = (
        'Traceback (most recent call last):\n'
        '  File "a.py", line 1, in f\n'
        '    do(x)\n'
        '    ^^^^^\n'
        'ValueError: bad'
    )
    pe = ParsedException.from_string(tb)
    assert len(pe.frames) == 1
    assert pe.exc_type == 'ValueError'
    assert pe.exc_msg == 'bad'
