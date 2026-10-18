# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Measure subject candidates against SUBJECTS.md. Run on kyiv-grid: uv run measure_subjects.py <workdir>"""
import json, re, subprocess, sys, time
from pathlib import Path

CANDIDATES = {
    "marshmallow": ("https://github.com/marshmallow-code/marshmallow", "src/marshmallow"),
    "click": ("https://github.com/pallets/click", "src/click"),
    "attrs": ("https://github.com/python-attrs/attrs", "src"),
    "arrow": ("https://github.com/arrow-py/arrow", "arrow"),
    "tomlkit": ("https://github.com/python-poetry/tomlkit", "tomlkit"),
    "python-slugify": ("https://github.com/un33k/python-slugify", "slugify"),
    "humanize": ("https://github.com/python-humanize/humanize", "src/humanize"),
    "cattrs": ("https://github.com/python-attrs/cattrs", "src/cattrs"),
    "jinja": ("https://github.com/pallets/jinja", "src/jinja2"),
    "itsdangerous": ("https://github.com/pallets/itsdangerous", "src/itsdangerous"),
    "boltons": ("https://github.com/mahmoud/boltons", "boltons"),
    "python-dateutil": ("https://github.com/dateutil/dateutil", "src/dateutil"),
    "tabulate": ("https://github.com/astanin/python-tabulate", "tabulate"),
    "pendulum": ("https://github.com/python-pendulum/pendulum", "src/pendulum"),
    "schedule": ("https://github.com/dbader/schedule", "schedule"),
}
FIX = re.compile(r"\b(fix|fixes|fixed|bug|regression|issue #?\d+)\b", re.I)
PERMISSIVE = ("MIT", "BSD", "Apache")


def sh(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def product_lines(root: Path) -> int:
    n = 0
    for p in root.rglob("*.py"):
        if "test" in p.parts[-1] or any(part in ("tests", "test") for part in p.parts):
            continue
        n += sum(1 for line in p.read_text(errors="ignore").splitlines() if line.strip())
    return n


def licence(repo: Path) -> str:
    for name in ("LICENSE", "LICENSE.txt", "LICENSE.md", "LICENSE.rst", "COPYING"):
        f = repo / name
        if f.exists():
            t = f.read_text(errors="ignore")
            if "Apache License" in t:
                return "Apache"
            if "Permission is hereby granted, free of charge" in t:
                return "MIT"
            if "Redistribution and use in source and binary forms" in t:
                return "BSD"
            return "other"
    return "missing"


def window(repo: Path, pkg: str):
    _, out = sh(f"git log --no-merges --format=%H%x09%s -- {pkg}", cwd=repo)
    commits = []
    for line in out.splitlines():
        h, _, s = line.partition("\t")
        _, files = sh(f"git show --name-only --format= {h}", cwd=repo)
        if any(f.startswith(pkg) and f.endswith(".py") for f in files.split()):
            commits.append((h, s))
        if len(commits) == 120:
            break
    fixes = sum(1 for _, s in commits if FIX.search(s))
    return len(commits), fixes


def tests(repo: Path):
    venv = repo / ".venv"
    sh(f"uv venv -q {venv}", cwd=repo)
    py = venv / "bin" / "python"
    # Install every test dependency the project declares: extras, PEP 735 groups, requirement files.
    sh(f"uv pip install -q --python {py} -e . pytest", cwd=repo)
    for e in ("tests", "test", "testing", "dev"):
        sh(f"uv pip install -q --python {py} -e '.[{e}]'", cwd=repo)
        sh(f"uv pip install -q --python {py} --group {e}", cwd=repo)
    for req in ("requirements/tests.txt", "requirements-test.txt", "requirements/test.txt",
                "requirements-dev.txt", "requirements/tests.in", "test-requirements.txt", "requirements-tests.txt"):
        if (repo / req).exists():
            sh(f"uv pip install -q --python {py} -r {req}", cwd=repo)
    t0 = time.time()
    code, out = sh(f"{py} -m pytest -q -x -p no:cacheprovider", cwd=repo, timeout=600)
    dt = time.time() - t0
    tail = out.strip().splitlines()[-1] if out.strip() else ""
    return code, round(dt, 1), tail


def main():
    work = Path(sys.argv[1]).expanduser()
    work.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[2:])
    rows = []
    for name, (url, pkg) in CANDIDATES.items():
        if only and name not in only:
            continue
        repo = work / name
        if not repo.exists():
            sh(f"git clone -q {url} {repo}")
        row: dict = {"name": name, "url": url, "pkg": pkg}
        try:
            row["head"] = sh("git rev-parse HEAD", cwd=repo)[1].strip()
            row["licence"] = licence(repo)
            row["product_lines"] = product_lines(repo / pkg) if (repo / pkg).exists() else None
            row["window_commits"], row["window_fixes"] = window(repo, pkg)
            row["pytest_code"], row["pytest_seconds"], row["pytest_tail"] = tests(repo)
        except Exception as exc:  # recorded, not hidden
            row["error"] = repr(exc)
        lic_ok = row.get("licence", "").startswith(PERMISSIVE)
        pl = row.get("product_lines") or 0
        row["eligible"] = bool(lic_ok and 4000 <= pl <= 30000 and row.get("pytest_code") == 0
                               and (row.get("pytest_seconds") or 999) < 120
                               and row.get("window_commits") == 120 and (row.get("window_fixes") or 0) >= 15)
        rows.append(row)
        print(json.dumps(row), flush=True)
    (work / "subjects.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
