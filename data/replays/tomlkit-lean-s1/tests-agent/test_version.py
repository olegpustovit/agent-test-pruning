import re

from pathlib import Path

import tomlkit


def test_version_matches_pyproject():
    text = (Path(__file__).parents[2] / "pyproject.toml").read_text(encoding="utf-8")
    doc = tomlkit.parse(text)
    assert tomlkit.__version__ == doc["project"]["version"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", tomlkit.__version__)
