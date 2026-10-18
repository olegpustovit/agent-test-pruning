# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Reintroduce real bugs at the end of a replayed stream and record which tests catch them.

A fault is the reverse of a bug-fix commit's product diff, applied to the final tree. Bug fixes inside the
window were shown to the agent ("seen"); bug fixes from before the window were not ("unseen"). A test
catches a fault when it fails with an exception other than an import or name error (those mean the revert
removed something the test imports, not that the test checks the behaviour).

uv run faults.py <run_dir> <pkg> <out_dir> [--tests tests/agent] [--unseen 60] [--workers 16]
"""
import argparse, json, re, shutil, subprocess, tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

FIX = re.compile(r"\b(fix|fixes|fixed|bug|regression|issue #?\d+)\b", re.I)
TEST_PATH = re.compile(r"(^|/)(tests?|testing)/|(^|/)(test_[^/]*|[^/]*_test|conftest)\.py$")
NOT_A_CATCH = ("ImportError", "ModuleNotFoundError", "NameError", "AttributeError: module")


def sh(cmd, cwd=None, timeout=900, inp=None):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout, input=inp)
    return r.returncode, r.stdout + r.stderr


def fixes(repo: Path, pkg: str, revs):
    out = []
    for h in revs:
        _, msg = sh(f"git log -1 --format=%s {h}", cwd=repo)
        _, files = sh(f"git show --name-only --format= {h}", cwd=repo)
        prod = [f for f in files.split() if f.startswith(pkg) and f.endswith(".py") and not TEST_PATH.search(f)]
        if FIX.search(msg) and prod:
            out.append({"commit": h, "subject": msg.strip(), "files": prod})
    return out


WORK = {}


def init_worker(repo, tests):
    d = Path(tempfile.mkdtemp(prefix="flt-"))
    tree = d / "repo"
    shutil.copytree(repo, tree, symlinks=True)
    site = tree / ".venv"
    for f in list(site.rglob("*.pth")) + list(site.rglob("__editable__*.py")):
        f.write_text(f.read_text().replace(str(repo), str(tree)))
    WORK.update(tree=tree, py=tree / ".venv/bin/python", tests=tests)


def run_fault(job):
    tree, py, tests = WORK["tree"], WORK["py"], WORK["tests"]
    files = " ".join(f"'{f}'" for f in job["files"])
    _, patch = sh(f"git diff {job['commit']} {job['commit']}^ -- {files}", cwd=tree)
    how = "clean"
    if sh("git apply --check -", cwd=tree, inp=patch)[0] == 0:
        sh("git apply -", cwd=tree, inp=patch)
    elif sh("git apply -3 -", cwd=tree, inp=patch)[0] == 0 and "<<<<<<<" not in sh(f"cat {files}", cwd=tree)[1]:
        how = "3way"
    else:
        sh(f"git checkout HEAD -- {files}; git reset -q", cwd=tree)
        return {**job, "applies": False}
    try:
        rc, out = sh(f"timeout 600 {py} -m pytest -q -p no:cacheprovider --tb=no -rfE {tests}", cwd=tree, timeout=700)
    finally:
        sh(f"git checkout HEAD -- {files}; git reset -q", cwd=tree)
    caught, other = [], []
    for m in re.finditer(r"^(FAILED|ERROR) (\S+)(?: - (.*))?$", out, re.M):
        kind, node, why = m.group(1), m.group(2), m.group(3) or ""
        (other if kind == "ERROR" or why.startswith(NOT_A_CATCH) else caught).append(node)
    return {**job, "applies": True, "how": how, "rc": rc, "caught_by": sorted(set(caught)), "failed_other": sorted(set(other))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir"); ap.add_argument("pkg"); ap.add_argument("out")
    ap.add_argument("--tests", default="tests/agent")
    ap.add_argument("--unseen", type=int, default=60, help="how many pre-window bug fixes to try, newest first")
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    run, out = Path(a.run_dir).resolve(), Path(a.out).resolve()
    repo = run / "repo"
    out.mkdir(parents=True, exist_ok=True)
    window = json.loads((run / "config.json").read_text())["window"]
    _, older = sh(f"git log --no-merges --format=%H {window[0]}^ -- {a.pkg}", cwd=repo)
    seen = [dict(f, kind="seen") for f in fixes(repo, a.pkg, window)]
    unseen = [dict(f, kind="unseen") for f in fixes(repo, a.pkg, older.split()[:400])][: a.unseen]
    jobs = seen + unseen
    print(f"{len(seen)} seen, {len(unseen)} unseen candidate faults", flush=True)
    with ProcessPoolExecutor(a.workers, initializer=init_worker, initargs=(repo, a.tests)) as ex, \
            (out / "faults.jsonl").open("w") as fh:
        for r in ex.map(run_fault, jobs):
            fh.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
