import pytest
from boltons.strutils import singularize


@pytest.mark.parametrize('word', ['glass', 'boss', 'class', 'kiss', 'address'])
def test_double_s_singular_unchanged(word):
    assert singularize(word) == word


def test_case_preserved():
    assert singularize('Glass') == 'Glass'
    assert singularize('BOSS') == 'BOSS'


def test_sses_plurals():
    assert singularize('glasses') == 'glass'
    assert singularize('Glasses') == 'Glass'
    assert singularize('bosses') == 'boss'
    assert singularize('classes') == 'class'


@pytest.mark.parametrize('word', ['glass', 'boss', 'glasses', 'kisses'])
def test_idempotent(word):
    once = singularize(word)
    assert singularize(once) == once


def test_regular_plurals_unaffected():
    assert singularize('cats') == 'cat'
    assert singularize('activities') == 'activity'
