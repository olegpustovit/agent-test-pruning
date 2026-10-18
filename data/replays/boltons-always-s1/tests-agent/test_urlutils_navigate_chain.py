from boltons.urlutils import URL


def test_navigate_relative_after_from_parts_tuple_path():
    # path_parts given as a tuple used to raise TypeError (list + tuple)
    url = URL.from_parts(scheme='https', host='host', path_parts=('a', 'b'))
    assert isinstance(url.path_parts, tuple)
    assert url.navigate('c').to_text() == 'https://host/a/c'


def test_navigate_chained_relative():
    url = URL('https://host/a/b')
    assert url.navigate('c').navigate('d').to_text() == 'https://host/a/d'


def test_navigate_chained_from_navigated_result():
    url = URL('https://host/a/b').navigate('c/d')
    assert url.navigate('e').to_text() == 'https://host/a/c/e'
