import re
from pathlib import Path

import tomlkit


ROOT = Path(__file__).resolve().parents[2]


def test_version_value():
    assert tomlkit.__version__ == "0.15.2"


def test_version_matches_pyproject():
    doc = tomlkit.parse((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert doc["project"]["version"] == tomlkit.__version__


def test_version_format():
    assert re.fullmatch(r"\d+\.\d+\.\d+", tomlkit.__version__)


def test_changelog_top_section_is_current_release():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert text.index("## [0.15.2] - 2026-10-16") < text.index("## [0.15.1] - 2026-07-17")
    assert text.index("## [0.15.1] - 2026-07-17") < text.index("## [0.15.0] - 2026-05-10")
    assert text.index("## [0.15.0] - 2026-05-10") < text.index("## [0.14.0] - 2026-01-13")
    assert text.index("## [0.14.0] - 2026-01-13") < text.index("## [0.13.3] - 2025-06-05")
    assert text.index("## [0.13.3] - 2025-06-05") < text.index("## [0.13.2] - 2024-08-14")
    assert text.index("## [Unreleased]") < text.index("## [0.15.2] - 2026-10-16")
    assert "pull/456))" in text
    assert text.index("## [0.13.2] - 2024-08-14") < text.index("## [0.13.1] - 2024-08-14") < text.index("## [0.13.0] - 2024-07-10")
    assert text.index("## [0.13.0] - 2024-07-10") < text.index("## [0.12.5] - 2024-05-08")
    assert "#333" in text
    assert "#355" in text


def test_changelog_unreleased_link_points_to_current_version():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    v = tomlkit.__version__
    assert f"[unreleased]: https://github.com/python-poetry/tomlkit/compare/{v}...master" in text
    assert f"[{v}]: https://github.com/python-poetry/tomlkit/releases/tag/{v}" in text


def test_pyproject_urls_point_to_python_poetry():
    doc = tomlkit.parse((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    urls = doc["project"]["urls"]
    assert urls["Homepage"] == "https://github.com/python-poetry/tomlkit"
    assert urls["Repository"] == "https://github.com/python-poetry/tomlkit"


def test_pyproject_pep621_metadata():
    doc = tomlkit.parse((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = doc["project"]
    assert project["name"] == "tomlkit"
    assert project["license"] == "MIT"
    assert project["requires-python"] == ">=3.9"
    assert [a["name"] for a in project["authors"]] == ["Sébastien Eustace", "Frost Ming"]
    assert "version" not in doc["tool"]["poetry"]
    assert "dependencies" not in doc["tool"]["poetry"]
    assert doc["build-system"]["requires"] == ["poetry-core>=2.2.0"]
