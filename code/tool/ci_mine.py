# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Catch labels from a repository's GitHub Actions history (the method's CI signal).

For each failed run: the tests that failed (from the failed-job log), and the next successful run on the same
branch. A failing test is labelled a *catch* when the change between the failing and the next green commit did not
edit that test's file (the product was fixed); a *test edit* when it did; *unknown* when no later green run or diff
exists. Output: one JSON line per (run, test).

uv run ci_mine.py <owner/repo> <local clone> <out.jsonl> [--limit 1000]
"""
import argparse, json, re, subprocess
from pathlib import Path

GO_FAIL = re.compile(r"--- FAIL: (Test\w+)")
GO_PKG = re.compile(r"^(?:FAIL|ok)\s+(\S+)\s", re.M)
PY_FAIL = re.compile(r"FAILED (\S+?\.py::\S+)")
BUN_FAIL = re.compile(r"\(fail\) (.+?) \[")


def sh(cmd, cwd=None, timeout=600):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo"); ap.add_argument("clone"); ap.add_argument("out")
    ap.add_argument("--limit", type=int, default=1000)
    a = ap.parse_args()
    clone = Path(a.clone).resolve()
    _, mod = sh("go list -m 2>/dev/null", cwd=clone)
    mod = mod.strip()
    _, js = sh(f"gh run list --repo {a.repo} --limit {a.limit} --json databaseId,headSha,headBranch,conclusion,createdAt,workflowName")
    runs = sorted(json.loads(js), key=lambda r: r["createdAt"])
    out = open(a.out, "w")
    for i, r in enumerate(runs):
        if r["conclusion"] != "failure":
            continue
        nxt = next((s for s in runs[i + 1:] if s["headBranch"] == r["headBranch"] and s["workflowName"] == r["workflowName"]
                    and s["conclusion"] == "success"), None)
        _, log = sh(f"gh run view {r['databaseId']} --repo {a.repo} --log-failed", timeout=300)
        tests = []
        # Go: attribute each "--- FAIL: TestX" to the package line that follows it in the log
        pending = []
        for line in log.splitlines():
            m = GO_FAIL.search(line)
            if m:
                pending.append(m.group(1)); continue
            m = re.search(r"\bFAIL\s+(\S+/\S+|\S+)\s+[\d.]+s", line)
            if m and pending:
                pkg = m.group(1)
                # strip the module path, also an older one (the module was renamed with the GitHub account)
                rel = re.sub(r"^github\.com/[^/]+/[^/]+/?", "", pkg) or "."
                tests += [f"{rel}::{t}" for t in pending]
                pending = []
        tests += PY_FAIL.findall(log)
        tests = sorted(set(tests))
        changed = None
        if nxt:
            sh(f"git fetch -q origin {r['headSha']} {nxt['headSha']}", cwd=clone)
            code, diff = sh(f"git diff --name-only {r['headSha']} {nxt['headSha']}", cwd=clone)
            changed = diff.split() if code == 0 else None
        for t in tests or ["<none parsed>"]:
            label = "unknown"
            if changed is not None and t != "<none parsed>":
                d = t.split("::")[0]
                test_files = [f for f in changed if f.startswith(d + "/") and f.endswith("_test.go")] if not d.endswith(".py") else [f for f in changed if f == d]
                label = "test_edit" if test_files else "catch"
            out.write(json.dumps({"run": r["databaseId"], "sha": r["headSha"], "at": r["createdAt"], "branch": r["headBranch"],
                                  "workflow": r["workflowName"], "test": t, "label": label,
                                  "fixed_by": nxt["headSha"] if nxt else None}) + "\n")
        out.flush()
        print(r["databaseId"], len(tests), "tests", "next green" if nxt else "no green", flush=True)


if __name__ == "__main__":
    main()
