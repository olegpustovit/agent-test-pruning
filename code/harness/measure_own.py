# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test accumulation in the owner's own repositories: test vs product lines now and 90 days ago, agent-authored commits."""
import json, re, subprocess, sys
from pathlib import Path

CODE = re.compile(r"\.(go|rs|ts|tsx|js|py|ml|mli|swift|lua|dart)$")
TEST = re.compile(r"(_test\.go$|\.test\.[tj]sx?$|\.spec\.[tj]sx?$|(^|/)(tests?|__tests__|spec|testdata)/|(^|/)test_[^/]*\.py$|_test\.py$|Tests?/|_spec\.lua$|_test\.ml$)")
AGENT = re.compile(r"co-authored-by: (claude|codex|cursor|copilot|gemini|aider)|generated with \[?claude|🤖", re.I)


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True).stdout


def lines_at(repo, rev):
    t = p = 0
    files = [f for f in git(repo, "ls-tree", "-r", "--name-only", rev).split("\n") if CODE.search(f) and "vendor/" not in f and "node_modules/" not in f]
    for f in files:
        n = sum(1 for l in git(repo, "show", f"{rev}:{f}").splitlines() if l.strip())
        if TEST.search(f):
            t += n
        else:
            p += n
    return t, p


for repo in sorted(Path(sys.argv[1]).iterdir()):
    if not (repo / ".git").exists():
        continue
    head = git(repo, "rev-parse", "HEAD").strip()
    old = git(repo, "rev-list", "-1", "--before=90 days ago", "HEAD").strip()
    t1, p1 = lines_at(repo, head)
    t0, p0 = lines_at(repo, old) if old else (0, 0)
    log = git(repo, "log", "--format=%H%x00%B%x01")
    commits = [c for c in log.split("\x01") if c.strip()]
    agent = sum(1 for c in commits if AGENT.search(c))
    first = git(repo, "log", "--reverse", "--format=%ad", "--date=short").split("\n")[0]
    print(json.dumps({"repo": repo.name, "first": first, "commits": len(commits), "agent_commits": agent,
                      "test_lines": t1, "product_lines": p1, "test_lines_90d_ago": t0, "product_lines_90d_ago": p0}), flush=True)
