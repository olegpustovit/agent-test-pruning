import os
import socket
import getpass

import pytest

from boltons import ecoutils


def _boom(*a, **k):
    raise AssertionError('identifying lookup performed while scrubbing')


def test_scrub_skips_lookups(monkeypatch):
    monkeypatch.setattr(getpass, 'getuser', _boom)
    monkeypatch.setattr(socket, 'gethostname', _boom)
    monkeypatch.setattr(socket, 'getfqdn', _boom)
    monkeypatch.setattr(os, 'getcwd', _boom)
    prof = ecoutils.get_profile(scrub=True)
    for key in ('username', 'hostname', 'hostfqdn', 'cwd'):
        assert prof[key] == '-'
    assert prof['uname']['node'] == '-'
    assert prof['python']['bin'] == '-'
    assert prof['python']['argv'] == '-'


def test_no_scrub_performs_lookups(monkeypatch):
    monkeypatch.setattr(getpass, 'getuser', lambda: 'bob')
    monkeypatch.setattr(socket, 'gethostname', lambda: 'h')
    monkeypatch.setattr(socket, 'getfqdn', lambda: 'h.example')
    monkeypatch.setattr(os, 'getcwd', lambda: '/x')
    prof = ecoutils.get_profile(scrub=False)
    assert prof['username'] == 'bob'
    assert prof['hostname'] == 'h'
    assert prof['hostfqdn'] == 'h.example'
    assert prof['cwd'] == '/x'


def test_username_failure_falls_back(monkeypatch):
    monkeypatch.setattr(getpass, 'getuser', _boom)
    assert ecoutils.get_profile(scrub=False)['username'] == ''
