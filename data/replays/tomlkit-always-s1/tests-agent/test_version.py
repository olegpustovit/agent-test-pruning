import re

from pathlib import Path

import tomlkit


ROOT = Path(__file__).resolve().parents[2]


def test_version_is_0_15_2():
    assert tomlkit.__version__ == "0.15.2"


def test_pyproject_matches_package_version():
    doc = tomlkit.parse((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = doc["project"]
    assert project["version"] == tomlkit.__version__
    assert project["license"] == "MIT"
    assert project["requires-python"] == ">=3.9"
    assert [a["name"] for a in project["authors"]] == [
        "Sébastien Eustace",
        "Frost Ming",
    ]
    assert project["urls"]["Homepage"] == "https://github.com/python-poetry/tomlkit"
    assert project["urls"]["Repository"] == "https://github.com/python-poetry/tomlkit"
    assert "version" not in doc["tool"]["poetry"]
    assert "dependencies" not in doc["tool"]["poetry"]
    requires = doc["build-system"]["requires"]
    assert len(requires) == 1
    assert requires[0].startswith("poetry-core>=2.")


def test_changelog_has_release_entry():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [0.15.2] - 2026-10-16" in text
    assert "## [unreleased]" not in text
    assert (
        "[0.15.2]: https://github.com/python-poetry/tomlkit/releases/tag/0.15.2"
        in text
    )
    assert (
        "[0.15.1]: https://github.com/python-poetry/tomlkit/releases/tag/0.15.1"
        in text
    )
    assert (
        "[0.15.0]: https://github.com/python-poetry/tomlkit/releases/tag/0.15.0"
        in text
    )
    assert "compare/0.15.2...master" in text
    ref_links = re.findall(r"^\[[^\]]+\]: (\S+)$", text, re.M)
    assert ref_links
    assert all(link.startswith("https://github.com/python-poetry/tomlkit/") for link in ref_links)
