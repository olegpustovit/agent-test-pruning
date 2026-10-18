from boltons.strutils import args2sh, args2cmd


def test_args2sh_sep():
    assert args2sh(['a', 'b c', 'd'], sep=',') == "a,'b c',d"
    assert args2sh(['a', 'b'], sep='\n') == 'a\nb'
    assert args2sh(['a', 'b']) == 'a b'
    assert args2sh(['a'], sep=',') == 'a'
    assert args2sh([], sep=',') == ''


def test_args2cmd_sep():
    assert args2cmd(['a', 'b c', 'd'], sep=',') == 'a,"b c",d'
    assert args2cmd(['a', 'b'], sep='\n') == 'a\nb'
    assert args2cmd(['a', 'b']) == 'a b'
    assert args2cmd(['a'], sep=',') == 'a'
