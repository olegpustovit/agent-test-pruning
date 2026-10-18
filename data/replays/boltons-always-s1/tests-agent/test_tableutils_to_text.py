from boltons.tableutils import Table


def test_column_widths_follow_content():
    t = Table([['a', 'bbbbbb'], ['cc', 'd']], headers=['x', 'y'])
    lines = t.to_text().split('\n')
    assert lines[0] == 'x  |   y   '
    assert lines[1] == '---|-------'
    assert lines[2] == 'a  | bbbbbb'
    assert lines[3] == 'cc |   d   '


def test_more_rows_than_columns():
    t = Table([['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']], headers=['x', 'y'])
    assert t.to_text().split('\n')[2:] == ['a | b', 'c | d', 'e | f', 'g | h']


def test_without_headers_and_maxlen():
    t = Table([['abcdef', 'x'], ['y', 'z']], headers=['h1', 'h2'])
    lines = t.to_text(with_headers=False).split('\n')
    assert lines == ['abcdef | x', '  y    | z']
    assert len(t.to_text(maxlen=3).split('\n')[2].split(' | ')[0]) <= 3
