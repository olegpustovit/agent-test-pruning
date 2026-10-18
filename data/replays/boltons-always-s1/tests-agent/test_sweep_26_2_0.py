import io

from boltons.cacheutils import LRI, LRU, ThresholdCounter
from boltons.jsonutils import reverse_iter_lines
from boltons.strutils import bytes2human
from boltons.urlutils import URL


def test_reverse_iter_lines_text_not_detached(tmp_path):
    p = tmp_path / 'f.txt'
    p.write_bytes('a\nb\nc'.encode('utf-8'))
    with open(p, encoding='utf-8') as f:
        assert list(reverse_iter_lines(f)) == ['c', 'b', 'a']
        f.seek(0)
        assert f.read() == 'a\nb\nc'


def test_reverse_iter_lines_encoding(tmp_path):
    p = tmp_path / 'f.txt'
    p.write_bytes('é\nü'.encode('latin-1'))
    with open(p, 'rb') as f:
        assert list(reverse_iter_lines(f, encoding='latin-1')) == ['ü', 'é']
    with open(p, encoding='latin-1') as f:
        assert list(reverse_iter_lines(f)) == ['ü', 'é']


def test_reverse_iter_lines_bytes():
    assert list(reverse_iter_lines(io.BytesIO(b'a\nb'))) == [b'b', b'a']


def test_threshold_counter_update_mapping_and_most_common():
    tc = ThresholdCounter(threshold=0.001)
    tc.update({'a': 3, 'b': 1})
    assert tc['a'] == 3 and tc['b'] == 1
    assert tc.most_common() == [('a', 3), ('b', 1)]
    assert tc.most_common(1) == [('a', 3)]
    assert tc.most_common(0) == []
    assert tc.most_common(-1) == []


def test_lri_lru_update_variants():
    for cls in (LRI, LRU):
        c = cls(max_size=10)
        c.update()
        assert len(c) == 0
        c.update(x=1)
        assert c['x'] == 1
        c.update(c, y=2)
        assert c['y'] == 2
        c.update([('z', 3)], w=4)
        assert c['z'] == 3 and c['w'] == 4


def test_bytes2human_yotta():
    assert bytes2human(1024 ** 8) == '1Y'
    assert bytes2human(1024 ** 9) == '1024Y'
    assert bytes2human(1024) == '1K'


def test_get_authority_empty_username_with_password():
    u = URL('http://:secret@example.com/')
    assert u.get_authority(with_userinfo=True) == ':secret@example.com'
    assert u.get_authority() == "example.com"
