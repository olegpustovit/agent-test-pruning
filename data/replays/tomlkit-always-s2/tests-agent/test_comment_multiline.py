import pytest

from tomlkit import comment
from tomlkit import document
from tomlkit import dumps
from tomlkit import parse


def test_single_line_comment_unchanged():
    assert comment("hello").trivia.comment == "# hello"


def test_empty_comment():
    assert comment("").trivia.comment == "#"


def test_multiline_comment_prefixes_each_line():
    assert comment("a\nb").trivia.comment == "# a\n# b"


def test_multiline_comment_empty_lines_bare_hash():
    c = comment("a\n\nb")
    assert c.trivia.comment == "# a\n#\n# b"


def test_trailing_newline():
    assert comment("a\n").trivia.comment == "# a\n#"


@pytest.mark.parametrize("text", ["a\nb", "a\n\nb\nc"])
def test_multiline_comment_in_document_is_valid_toml(text):
    doc = document()
    doc.add(comment(text))
    doc.add("key", "value")
    out = dumps(doc)
    reparsed = parse(out)
    assert reparsed["key"] == "value"
    for line in out.splitlines():
        assert line.lstrip().startswith(("#", "key"))
