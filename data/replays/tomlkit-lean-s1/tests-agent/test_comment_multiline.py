import tomlkit

from tomlkit import comment


def test_multiline_comment_prefixes_every_line():
    assert comment("a\nb").as_string() == "# a\n# b\n"


def test_multiline_comment_empty_line_is_bare_hash():
    assert comment("a\n\nb").as_string() == "# a\n#\n# b\n"


def test_single_line_comment_unchanged():
    assert comment("a").as_string() == "# a\n"


def test_multiline_comment_roundtrips_as_valid_toml():
    doc = tomlkit.document()
    doc.add(comment("first\nsecond\n\nfourth"))
    doc.add("a", 1)
    parsed = tomlkit.parse(tomlkit.dumps(doc))
    assert parsed == {"a": 1}
