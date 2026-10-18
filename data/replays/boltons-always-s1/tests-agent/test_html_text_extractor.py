from boltons.strutils import HTMLTextExtractor, html2text


def test_extractor_init_state():
    e = HTMLTextExtractor()
    assert e.result == []
    assert e.convert_charrefs is True
    assert e.get_text() == ''


def test_extractor_feed_and_close():
    e = HTMLTextExtractor()
    e.feed('<p>Hello &amp; ')
    e.feed('<b>world</b></p>')
    e.close()
    assert e.get_text() == 'Hello & world'


def test_html2text_entities_and_tags():
    assert html2text('<a href="#">Test &amp;<em>(&#x3b7;&#956;)</em></a>') == 'Test &(ημ)'


def test_html2text_plain_and_empty():
    assert html2text('') == ''
    assert html2text('no tags') == 'no tags'


def test_instances_independent():
    a, b = HTMLTextExtractor(), HTMLTextExtractor()
    a.feed('x')
    assert b.get_text() == ''
