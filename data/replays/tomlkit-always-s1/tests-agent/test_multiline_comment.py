import pytest

import tomlkit

from tomlkit import comment


@pytest.mark.parametrize(
    "text, expected",
    [
        ("hello", "# hello"),
        ("", "#"),
        ("a\nb", "# a\n# b"),
        ("a\n\nb", "# a\n#\n# b"),
        ("a\n", "# a\n#"),
        ("\na", "#\n# a"),
    ],
)
def test_comment_rendering(text, expected):
    assert comment(text).as_string() == expected + "\n"


def test_multiline_comment_in_document_is_valid_toml():
    doc = tomlkit.document()
    doc.add(comment("line one\n\nline three"))
    doc.add("key", "value")
    out = tomlkit.dumps(doc)
    parsed = tomlkit.parse(out)
    assert parsed == {"key": "value"}
    assert all(
        line.startswith("#") or not line or "=" in line for line in out.splitlines()
    )
