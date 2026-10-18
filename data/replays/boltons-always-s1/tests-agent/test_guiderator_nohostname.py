import socket

from boltons.iterutils import GUIDerator, SequentialGUIDerator


def test_empty_hostname_uses_placeholder(monkeypatch):
    monkeypatch.setattr(socket, 'gethostname', lambda: '')
    g = GUIDerator()
    assert '<nohostname>' in g.salt
    assert isinstance(g.salt, str)
    assert len(next(g)) == 24


def test_empty_hostname_sequential(monkeypatch):
    monkeypatch.setattr(socket, 'gethostname', lambda: '')
    g = SequentialGUIDerator()
    assert '<nohostname>' in g.salt
    assert len(next(g)) == 24


def test_hostname_used_when_present(monkeypatch):
    monkeypatch.setattr(socket, 'gethostname', lambda: 'myhost')
    g = GUIDerator()
    assert 'myhost' in g.salt
    assert '<nohostname>' not in g.salt
