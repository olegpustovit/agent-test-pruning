# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Replay a subject's real commit history while a coding agent writes the tests.

At each window commit: product files are set to their upstream state; earlier agent tests that now
fail are reported to the agent; the agent adds tests for the change under tests/agent/; edits outside
tests/agent/ are reverted; agent tests that still fail are rolled back to the previous step; then the
human test changes of the commit are applied, and the step is committed with its metadata.

uv run replay.py <subject_clone> <pkg> <run_dir> --variant always|lean --seed N [--agent claude|stub] [--model M]
"""
import argparse, json, re, shlex, shutil, subprocess, time
from pathlib import Path

AGENT_DIR = "tests/agent"
TEST_PATH = re.compile(r"(^|/)(tests?|testing)/|(^|/)(test_[^/]*|[^/]*_test|conftest)\.py$")
MODEL = "claude-sonnet-5-5"

PROMPTS = {
    "always": (
        "You maintain the test suite of this repository. The commit below was just applied to the product code.\n"
        "Add tests for this change. Put every new or changed test under {agent_dir}/ (create files as you like). "
        "Run them with `{py} -m pytest {agent_dir} -q` and make sure they pass. "
        "Do not edit any file outside {agent_dir}/.\n"
    ),
    "lean": (
        "You maintain the test suite of this repository. The commit below was just applied to the product code.\n"
        "Add tests for this change only where the existing tests do not already check it; adding no test is fine. "
        "Put every new or changed test under {agent_dir}/. "
        "Run them with `{py} -m pytest {agent_dir} -q` and make sure they pass. "
        "Do not edit any file outside {agent_dir}/.\n"
    ),
}


def sh(cmd, cwd=None, timeout=1800, check=False):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode:
        raise RuntimeError(f"{cmd}: {r.stdout}{r.stderr}")
    return r.returncode, r.stdout + r.stderr


def window(src: Path, pkg: str, n: int):
    _, out = sh(f"git log --no-merges --format=%H -- {pkg}", cwd=src)
    commits = []
    for h in out.split():
        _, files = sh(f"git show --name-only --format= {h}", cwd=src)
        if any(f.startswith(pkg) and f.endswith(".py") for f in files.split()):
            commits.append(h)
        if len(commits) == n:
            break
    return list(reversed(commits))


def changed(repo: Path, rev: str, base: str | None = None):
    """Paths that differ between base (default: the commit's parent) and rev."""
    _, out = sh(f"git diff --name-status --no-renames {base or rev + '^'} {rev}", cwd=repo)
    rows = []
    for line in out.splitlines():
        status, _, path = line.partition("\t")
        rows.append((status[0], path))
    return rows


def set_paths(repo: Path, rev: str, rows):
    for status, path in rows:
        if status == "D":
            sh(f"git rm -q --cached --ignore-unmatch -- '{path}'", cwd=repo)
            (repo / path).unlink(missing_ok=True)
        else:
            sh(f"git checkout {rev} -- '{path}'", cwd=repo, check=True)


def failing_files(repo: Path, py: Path):
    if not (repo / AGENT_DIR).exists():
        return 0, []
    _, out = sh(f"prlimit --as=3221225472 {py} -m pytest {AGENT_DIR} -q -p no:cacheprovider -rf --tb=no --timeout=60", cwd=repo, timeout=1800)
    files = sorted({m.group(1) for m in re.finditer(r"^(?:FAILED|ERROR) (\S+?\.py)", out, re.M)})
    n = re.search(r"(\d+) passed", out)
    return (int(n.group(1)) if n else 0), files


def human_suite(repo: Path, py: Path):
    _, out = sh(f"prlimit --as=3221225472 {py} -m pytest -q -p no:cacheprovider --tb=no --timeout=60 --ignore={AGENT_DIR}", cwd=repo, timeout=1800)
    get = lambda k: int(m.group(1)) if (m := re.search(rf"(\d+) {k}", out)) else 0
    return {"passed": get("passed"), "failed": get("failed"), "errors": get("error")}


def agent_lines(repo: Path):
    d = repo / AGENT_DIR
    if not d.exists():
        return 0, 0
    lines = files = 0
    for p in d.rglob("*.py"):
        files += 1
        lines += sum(1 for l in p.read_text(errors="ignore").splitlines() if l.strip())
    return files, lines


def wait_for_memory(min_mb=1500):
    """Hold the next agent session while the machine is short of memory (8 GB box, several streams)."""
    while True:
        avail = next(int(l.split()[1]) // 1024 for l in open("/proc/meminfo") if l.startswith("MemAvailable"))
        if avail >= min_mb:
            return
        time.sleep(20)


def run_agent(kind, repo, prompt, log, model=MODEL):
    wait_for_memory()
    t0 = time.time()
    if kind == "stub":
        return {"seconds": 0.0, "stub": True}
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "json",
           "--dangerously-skip-permissions", "--no-session-persistence",
           "--strict-mcp-config"]  # no MCP servers: the agent does not need them, and each costs memory
    try:
        r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=1500, stdin=subprocess.DEVNULL)
        out = r.stdout
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        if isinstance(out, bytes):
            out = out.decode(errors="ignore")
    log.write_text(out)
    meta = {"seconds": round(time.time() - t0, 1)}
    try:
        j = json.loads(out)
        meta.update({k: j.get(k) for k in ("total_cost_usd", "num_turns", "is_error", "usage", "model")})
    except Exception:
        meta["unparsed"] = True
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("pkg"); ap.add_argument("run_dir")
    ap.add_argument("--variant", default="always", choices=PROMPTS)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--agent", default="claude", choices=["claude", "stub"])
    ap.add_argument("--commits", type=int, default=120)
    ap.add_argument("--model", default=MODEL, help="agent model for claude -p")
    ap.add_argument("--limit", type=int, default=0, help="stop after this many steps (smoke test)")
    ap.add_argument("--python", default="3.11", help="one interpreter for the whole window")
    ap.add_argument("--extra-deps", default="", help="test dependencies the start commit does not declare")
    a = ap.parse_args()
    src, run = Path(a.src).expanduser().resolve(), Path(a.run_dir).expanduser().resolve()
    repo, logs = run / "repo", run / "logs"
    commits = window(src, a.pkg, a.commits)
    state = run / "state.jsonl"
    if not repo.exists():
        logs.mkdir(parents=True, exist_ok=True)
        sh(f"git clone -q --no-hardlinks {src} {repo}", check=True)
        sh(f"git checkout -q -b bench {commits[0]}^", cwd=repo, check=True)
        sh("git submodule update --init -q", cwd=repo)
        with (repo / ".git/info/exclude").open("a") as fh:
            fh.write("\n__pycache__/\n*.pyc\n.venv/\n.cov.json\n.reach-cov.json\n.coverage*\n.pytest_cache/\n")
        (repo / AGENT_DIR).mkdir(parents=True, exist_ok=True)
        (repo / AGENT_DIR / "__init__.py").touch()
        sh(f"git add {AGENT_DIR} && git -c user.name=bench -c user.email=bench@local commit -qm 'bench: start' --allow-empty", cwd=repo)
        (run / "config.json").write_text(json.dumps({**vars(a), "window": commits}, indent=1))
    py = repo / ".venv/bin/python"
    # A resumed run starts from the last committed step: drop any half-done step.
    sh("git checkout -q -f bench && git reset -q --hard && git clean -fdq", cwd=repo)
    if not py.exists():
        sh(f"uv venv -q --python {a.python} {repo/'.venv'}", cwd=repo, check=True)
        sh(f"uv pip install -q --python {py} -e . pytest", cwd=repo)
        for e in ("tests", "test", "testing", "dev"):
            sh(f"uv pip install -q --python {py} -e '.[{e}]'", cwd=repo)
            sh(f"uv pip install -q --python {py} --group {e}", cwd=repo)
        sh(f"uv pip install -q --python {py} pytest-timeout", cwd=repo, check=True)
        if a.extra_deps:
            sh(f"uv pip install -q --python {py} " + " ".join(shlex.quote(d) for d in a.extra_deps.split()), cwd=repo, check=True)
    done = {json.loads(l)["commit"] for l in state.read_text().splitlines()} if state.exists() else set()
    steps = 0
    for i, rev in enumerate(commits):
        if rev in done:
            continue
        # Bring every non-agent path to its upstream state at rev (this also carries the changes of
        # commits outside the window); the prompt shows only this commit's own product diff.
        rows = [r for r in changed(repo, rev, base="HEAD") if not r[1].startswith(AGENT_DIR)]
        product = [r for r in rows if not TEST_PATH.search(r[1])]
        human_tests = [r for r in rows if TEST_PATH.search(r[1])]
        own = [r for r in changed(repo, rev) if not TEST_PATH.search(r[1])]
        set_paths(repo, rev, product)
        _, broken = failing_files(repo, py)
        _, msg = sh(f"git log -1 --format=%B {rev}", cwd=repo)
        _, diff = sh(f"git diff {rev}^ {rev} -- " + " ".join(f"'{p}'" for _, p in own), cwd=repo)
        prompt = PROMPTS[a.variant].format(agent_dir=AGENT_DIR, py=py)
        if broken:
            prompt += ("\nAfter this change, these existing test files under " + AGENT_DIR +
                       " fail: " + ", ".join(broken) + ". Fix or remove what the change made wrong.\n")
        prompt += f"\nCommit message:\n{msg.strip()}\n\nProduct diff:\n{diff[:60000]}\n"
        # Snapshot of the intended tree before the agent runs (product at rev, agent tests so far).
        sh("git add -A", cwd=repo)
        snap = sh("git write-tree", cwd=repo)[1].strip()
        meta = run_agent(a.agent, repo, prompt, logs / f"{i:03d}-{rev[:8]}.json", a.model)
        if meta.get("is_error") or meta.get("unparsed"):
            # never record a step the agent did not do; leave the tree for a rerun of this commit
            raise SystemExit(f"agent failed at step {i} ({rev[:12]}); see {logs}")
        # Put every path outside tests/agent/ back to the snapshot, whatever the agent did (edits, stash, deletes).
        sh("git stash clear", cwd=repo)
        sh("git add -A", cwd=repo)
        _, names = sh(f"git diff --cached --name-only --no-renames {snap}", cwd=repo)
        outside = [p for p in names.split() if not p.startswith(AGENT_DIR)]
        for p in outside:
            if sh(f"git cat-file -e {snap}:'{p}'", cwd=repo)[0] == 0:
                sh(f"git checkout {snap} -- '{p}'", cwd=repo, check=True)
            else:
                sh(f"git rm -q --cached --ignore-unmatch -- '{p}'", cwd=repo)
                pth = repo / p
                shutil.rmtree(pth) if pth.is_dir() else pth.unlink(missing_ok=True)
        _, still = failing_files(repo, py)
        rolled = []
        for f in still:  # roll failing agent files back to the previous step
            if sh(f"git cat-file -e HEAD:'{f}'", cwd=repo)[0] == 0:
                sh(f"git checkout HEAD -- '{f}'", cwd=repo)
            else:
                (repo / f).unlink(missing_ok=True)
            rolled.append(f)
        set_paths(repo, rev, human_tests)
        sh("git submodule update --init -q", cwd=repo)  # gitlinks (e.g. spec-test data) follow the commit
        passed, _ = failing_files(repo, py)
        nfiles, nlines = agent_lines(repo)
        human = human_suite(repo, py)
        rec = {"i": i, "commit": rev, "agent": meta, "broken_before": broken, "outside_reverted": outside,
               "rolled_back": rolled, "agent_tests_passed": passed, "agent_files": nfiles, "agent_lines": nlines, "human": human}
        sh(f"git add -A && git -c user.name=bench -c user.email=bench@local commit -q --allow-empty -m 'bench {i}: {rev[:12]}'", cwd=repo, check=True)
        rec["bench_head"] = sh("git rev-parse HEAD", cwd=repo)[1].strip()
        _, drift = sh(f"git diff --name-only {rev} HEAD -- . ':!{AGENT_DIR}'", cwd=repo)
        if drift.strip():  # the product must equal upstream at every step
            raise SystemExit(f"step {i}: tree differs from upstream {rev[:12]}: {drift.split()[:5]}")
        with state.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps({k: rec[k] for k in ("i", "commit", "agent_tests_passed", "agent_lines", "rolled_back", "human")}), flush=True)
        steps += 1
        if a.limit and steps >= a.limit:
            break


if __name__ == "__main__":
    main()
