from boltons.strutils import HTMLTextExtractor, html2text


def test_extractor_init_converts_charrefs():
    ex = HTMLTextExtractor()
    assert ex.convert_charrefs is True
    assert ex.result == []


def test_html2text_basic():
    assert html2text('<p>Hello <b>world</b></p>') == 'Hello world'


def test_html2text_entities_and_charrefs():
    assert html2text('a &amp; b &#65; &#x42; &lt;') == 'a & b A B <'


def test_html2text_unknown_entity_kept():
    assert html2text('x &bogus; y') == 'x &bogus; y'


def test_extractor_is_reusable_after_reset():
    ex = HTMLTextExtractor()
    ex.feed('<i>one</i>')
    ex.close()
    assert ex.get_text() == 'one'
