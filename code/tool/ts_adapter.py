# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""testprune inputs for a TypeScript/Bun repository whose tests are fixture files (xi's tools/verify-suite.ts).

Writes the same files as go_adapter.py (reach.json, mut/kills.jsonl, mut/tests.json, flt/faults.jsonl),
so testprune.py rank/evaluate work unchanged. The unit of pruning is one fixture file; test id "<path>::file".
Reach is static: a fixture reaches every product file in its transitive import graph, and every function in it.

uv run ts_adapter.py reach  <repo> <out_dir> [--workers 8]
uv run ts_adapter.py mutate <repo> <out_dir> [--per-file 12] [--seed 1] [--workers 8]
uv run ts_adapter.py faults <repo> <out_dir> [--max 150] [--workers 8]

Environment: BUN (default ~/.bun-new/bin/bun), WORKDIR (worker copies, default <out_dir>/../work-<name>).
"""
import argparse, json, os, random, re, shutil, signal, subprocess, threading, time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HELPER = Path(__file__).parent / "tshelper/tshelper.ts"
BUN = os.environ.get("BUN", str(Path.home() / ".bun-new/bin/bun"))
FIX = re.compile(r"\b(fix|fixes|fixed|bug|regression|issue #?\d+)\b", re.I)

# Suites and fixture roots of tools/verify-suite.ts (unit, services, ui, vim); .py fixtures are skipped.
STANDALONE_UNIT = ["verify.ts", "t010-text-fidelity.ts", "t011-transactions.ts", "t012-undo-history.ts", "t101-literal-controls.ts"]
SUITES = {
    "unit": ["tests/architecture", "tests/config", "tests/document", "tests/layout", "tests/persistence", "tests/platform",
             "tests/selections", "tests/workbench"],
    "vim": ["tests/vim", "tests/oracle"],
    "services": ["tests/files", "tests/formatting", "tests/git", "tests/lsp", "tests/search", "tests/services", "tests/syntax", "tests/tasks"],
    "ui": ["tests/ui"],
}
TEST_PRELOAD = "packages/ui/src/entrypoints/preload.ts"  # bunfig.toml [test] preload: loaded by every `bun test`


def sh(cmd, cwd=None, timeout=1800, inp=None):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout, input=inp)
    return r.returncode, r.stdout, r.stderr


def jl(text):
    return [json.loads(l) for l in text.splitlines() if l.strip().startswith("{")]


def helper(cmd, repo, files, chunk=200):
    out = []
    for i in range(0, len(files), chunk):
        r = subprocess.run([BUN, "run", str(HELPER), cmd, str(repo), *files[i:i + chunk]], capture_output=True, text=True,
                           env={**os.environ, "TSHELPER_PARSER_REPO": str(REPO_FOR_PARSER)})
        out += jl(r.stdout)
    return out


def discover(repo):
    def executable(suite, name):
        return name.endswith(".test.ts") or (suite == "unit" and name in STANDALONE_UNIT)
    found, skipped = set(), set()
    for suite, roots in SUITES.items():
        for root in roots:
            for p in sorted((repo / root).rglob("*")):
                if not p.is_file():
                    continue
                rel = str(p.relative_to(repo))
                if executable(suite, p.name):
                    found.add(rel)
                elif suite == "unit" and p.name.startswith("test_") and p.name.endswith(".py"):
                    skipped.add(rel)
    return sorted(found), sorted(skipped)


def is_product(f):
    parts = f.split("/")
    return (parts[0] in ("packages", "apps") and (f.endswith(".ts") or f.endswith(".tsx")) and not f.endswith(".d.ts")
            and not re.search(r"\.(test|spec|bench)\.tsx?$", f)
            and not any(p in ("test", "tests", "__tests__", "fixtures", "testdata", "node_modules") for p in parts))


def product_files(repo):
    _, out, _ = sh("git ls-files 'packages/*' 'apps/*'", cwd=repo)
    return [f for f in out.split() if is_product(f)]


def run_fixture(tree, fid, timeout):
    """Run one fixture the way verify-suite does; returns (passed, seconds, output tail)."""
    cmd = [BUN, "test", str(tree / fid)] if fid.endswith(".test.ts") else [BUN, "run", str(tree / fid)]
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, cwd=tree, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         env={**os.environ, "XDG_CONFIG_HOME": ""}, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=timeout)
        code = p.returncode
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        out, _ = p.communicate()
        code = -9
    try:
        os.killpg(p.pid, signal.SIGKILL)  # stray children of the fixture
    except ProcessLookupError:
        pass
    return code == 0, time.monotonic() - t0, out.decode(errors="replace")[-4000:]


class Pool:
    """Private copies of the repository (node_modules symlinked), reset to the clone's state at start."""

    def __init__(self, repo, out, n, name):
        base = Path(os.environ.get("WORKDIR", out.parent / f"work-{out.name}"))
        self.trees = []
        for i in range(n):
            d = base / f"{name}{i}"
            d.mkdir(parents=True, exist_ok=True)
            sh(f"rsync -a --delete --exclude=/node_modules --exclude=/.cache --exclude=/.artifacts '{repo}/' '{d}/'")
            if not (d / "node_modules").exists():
                (d / "node_modules").symlink_to(repo / "node_modules")
            self.trees.append(d)
        self.free = list(self.trees)
        self.lock = threading.Lock()

    def take(self):
        with self.lock:
            return self.free.pop()

    def give(self, t):
        with self.lock:
            self.free.append(t)


def bugfix_counts(repo):
    _, log, _ = sh("git log --no-merges --format=%x00%s --name-only", cwd=repo)
    fixes = defaultdict(int)
    for block in log.split("\x00")[1:]:
        ls = block.strip().splitlines()
        if ls and FIX.search(ls[0]):
            for f in ls[1:]:
                fixes[f.strip()] += 1
    return fixes


def cmd_reach(a):
    repo, out = Path(a.repo).resolve(), Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.monotonic()
    fixtures, skipped_py = discover(repo)
    print(f"{len(fixtures)} fixtures, {len(skipped_py)} .py skipped", flush=True)
    # 1) every fixture once in parallel private copies (the conditions of the mutation runs)
    pool = Pool(repo, out, a.workers, "w")
    res = {}

    def one(fid):
        t = pool.take()
        try:
            return fid, run_fixture(t, fid, a.head_timeout)
        finally:
            pool.give(t)
    with ThreadPoolExecutor(a.workers) as ex:
        for i, (fid, r) in enumerate(ex.map(one, fixtures)):
            res[fid] = r
            if not r[0]:
                print(f"  fail (parallel) {fid} {r[1]:.1f}s", flush=True)
    # 2) a fixture that failed is run again alone (no other fixture running); failing alone = failing at head,
    #    passing alone = flaky under parallel load; both are left out
    failing, flaky = [], []
    for fid in [f for f in fixtures if not res[f][0]]:
        ok, secs, tail = run_fixture(pool.trees[0], fid, a.head_timeout)
        (flaky if ok else failing).append(fid)
        print(f"  rerun alone {fid}: {'pass (flaky, left out)' if ok else 'fail'}", flush=True)
    passing = [f for f in fixtures if res[f][0]]
    tests = [f"{f}::file" for f in passing]
    print(f"{len(passing)} passing, {len(failing)} failing at head, {len(flaky)} flaky; {time.monotonic() - t_start:.0f}s", flush=True)

    prod = set(product_files(repo))
    entries = {f: [f] + ([TEST_PRELOAD] if f.endswith(".test.ts") else []) for f in passing}
    graph = {}
    for r in helper("graph", repo, sorted({e for es in entries.values() for e in es})):
        graph[r["entry"]] = r["files"]
    reached = {f: sorted({x for e in entries[f] for x in graph.get(e, []) if x in prod}) for f in passing}
    files = sorted({x for v in reached.values() for x in v})
    funcs = {r["file"]: r for r in helper("funcs", repo, sorted(prod))}
    fixes = bugfix_counts(repo)
    symbols = {f"{f}:{fn['name']}": {"file": f, "bugfixes": fixes.get(f, 0)} for f in sorted(prod) for fn in funcs.get(f, {}).get("funcs", [])}
    R = {}
    for f in passing:
        syms, ids = [], []
        for pf in reached[f]:
            syms += [f"{pf}:{fn['name']}" for fn in funcs.get(pf, {}).get("funcs", [])]
            ids += [f"{pf}:{n}" for n in funcs.get(pf, {}).get("body_lines", [])]
        R[f"{f}::file"] = {"symbols": sorted(syms), "lines": len(ids), "line_ids": sorted(ids), "files": reached[f]}
    sources = {f"{f}::file": (repo / f).read_text(errors="replace") for f in passing}
    secs = {f"{f}::file": round(res[f][1], 3) for f in passing}
    (out / "reach.json").write_text(json.dumps({
        "pkg": repo.name, "symbols": symbols, "tests": R, "sources": sources, "seconds": secs,
        "failing_at_head": sorted(failing), "flaky_at_head": sorted(flaky), "skipped_py": skipped_py,
        "product_files": sorted(prod), "reached_files": files,
        "head": sh("git rev-parse HEAD", cwd=repo)[1].strip()}))
    print(f"{len(tests)} passing fixtures ({len(failing)} failing at head, {len(flaky)} flaky, {len(skipped_py)} .py skipped), "
          f"{len(prod)} product files ({len(files)} reached), {len(symbols)} symbols; {time.monotonic() - t_start:.0f}s")


def by_file(R):
    m = defaultdict(set)
    for t, v in R["tests"].items():
        for f in v["files"]:
            m[f].add(t)
    return m


def run_selected(tree, tests, timeout):
    failed, outputs = set(), []
    for t in sorted(tests):
        ok, _, tail = run_fixture(tree, t.split("::")[0], timeout)
        if not ok:
            failed.add(t)
            outputs.append(tail)
    return failed, outputs


def cmd_mutate(a):
    repo, out = Path(a.repo).resolve(), Path(a.out).resolve()
    (out / "mut").mkdir(parents=True, exist_ok=True)
    R = json.loads((out / "reach.json").read_text())
    reach = by_file(R)
    files = sorted(reach)
    funcs = {r["file"]: set(r["body_lines"]) for r in helper("funcs", repo, files)}
    sites = defaultdict(list)
    for s in helper("sites", repo, files):
        if s["line"] in funcs.get(s["file"], ()):
            sites[s["file"]].append(s)
    rng = random.Random(a.seed)
    jobs = []
    for f in files:
        ss = sites[f]
        rng.shuffle(ss)
        for s in ss[: a.per_file]:
            jobs.append({**s, "id": f"{f}:{s['line']}:{s['start']}:{s['op']}", "tests": sorted(reach[f])})
    (out / "mut/tests.json").write_text(json.dumps(sorted(R["tests"])))
    (out / "mut/mutants.json").write_text(json.dumps([{k: v for k, v in j.items() if k != "tests"} for j in jobs]))
    kp = out / "mut/kills.jsonl"
    done = {json.loads(l)["id"] for l in kp.read_text().splitlines() if l.strip()} if kp.exists() else set()
    todo = [j for j in jobs if j["id"] not in done]
    print(f"{len(jobs)} mutants in {len(files)} reached files ({sum(len(v) for v in sites.values())} sites), "
          f"{len(done)} already done, {sum(len(j['tests']) for j in todo)} fixture runs to do", flush=True)
    pool = Pool(repo, out, a.workers, "w")

    def one(job):
        tree = pool.take()
        try:
            p = tree / job["file"]
            orig = p.read_bytes()
            assert orig[job["start"]:job["end"]].decode() == job["orig"], job["id"]
            p.write_bytes(orig[: job["start"]] + job["rep"].encode() + orig[job["end"]:])
            try:
                # invalid = the mutated file no longer parses (Bun strips types without checking them, so a parse
                # failure is the only way a mutant breaks every fixture at import time). Fixture output is not used for
                # this: a runtime "SyntaxError" (JSON.parse of bad data) is a real kill.
                rc = subprocess.run([BUN, "run", str(HELPER), "check", str(tree), job["file"]], capture_output=True,
                                    env={**os.environ, "TSHELPER_PARSER_REPO": str(repo)}).returncode
                if rc:
                    failed, status = set(), "invalid"
                else:
                    failed, _ = run_selected(tree, job["tests"], a.timeout)
                    status = "killed" if failed else "survived"
            finally:
                p.write_bytes(orig)
        finally:
            pool.give(tree)
        return {k: job[k] for k in ("id", "file", "line", "op", "orig", "rep")} | {
            "status": status, "failed": sorted(failed) if status != "invalid" else []}

    t0 = time.monotonic()
    counts = defaultdict(int)
    with ThreadPoolExecutor(a.workers) as ex, kp.open("a") as fh:
        for i, fut in enumerate(as_completed([ex.submit(one, j) for j in todo])):
            r = fut.result()
            fh.write(json.dumps(r) + "\n"); fh.flush()
            counts[r["status"]] += 1
            if i % 25 == 0:
                print(f"{i + 1}/{len(todo)} {dict(counts)} {time.monotonic() - t0:.0f}s", flush=True)
    print(f"done {dict(counts)} in {time.monotonic() - t0:.0f}s", flush=True)


def cmd_faults(a):
    """Revert each bug-fix commit's product change at HEAD; record which reaching fixtures then fail."""
    repo, out = Path(a.repo).resolve(), Path(a.out).resolve()
    (out / "flt").mkdir(parents=True, exist_ok=True)
    R = json.loads((out / "reach.json").read_text())
    reach = by_file(R)
    _, log, _ = sh("git log --no-merges --format=%H%x09%s", cwd=repo)
    jobs = []
    for line in log.splitlines():
        h, _, s = line.partition("\t")
        if not FIX.search(s):
            continue
        _, files, _ = sh(f"git show --name-only --format= {h}", cwd=repo)
        prod = [f for f in files.split() if is_product(f)]
        if prod:
            jobs.append({"commit": h, "subject": s, "files": prod, "kind": "history"})
        if len(jobs) >= a.max:
            break
    print(f"{len(jobs)} bug-fix commits touching product files", flush=True)
    pool = Pool(repo, out, a.workers, "w")

    def one(job):
        files = " ".join(f"'{f}'" for f in job["files"])
        _, patch, _ = sh(f"git diff {job['commit']} {job['commit']}^ -- {files}", cwd=repo)
        sel = set().union(*(reach.get(f, set()) for f in job["files"]))
        tree = pool.take()
        try:
            saved = {f: (tree / f).read_bytes() for f in job["files"] if (tree / f).exists()}
            code, _, _ = sh("patch -p1 --dry-run -s -f", cwd=tree, inp=patch)
            if code or not patch.strip():
                return {**job, "applies": False, "caught_by": [], "selected": len(sel)}
            sh("patch -p1 -s -f --no-backup-if-mismatch", cwd=tree, inp=patch)
            try:
                failed, _ = run_selected(tree, sel, a.timeout)
            finally:
                for f, b in saved.items():
                    (tree / f).write_bytes(b)
                for f in job["files"]:
                    if f not in saved:
                        (tree / f).unlink(missing_ok=True)
                for rej in list(tree.rglob("*.orig")) + list(tree.rglob("*.rej")):
                    if "node_modules" not in rej.parts:
                        rej.unlink()
        finally:
            pool.give(tree)
        return {**job, "applies": True, "caught_by": sorted(failed), "selected": len(sel)}

    t0 = time.monotonic()
    with ThreadPoolExecutor(a.workers) as ex, (out / "flt/faults.jsonl").open("w") as fh:
        for r in ex.map(one, jobs):
            fh.write(json.dumps(r) + "\n"); fh.flush()
    print(f"done in {time.monotonic() - t0:.0f}s", flush=True)


REPO_FOR_PARSER = None


def main():
    global REPO_FOR_PARSER
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("reach", "mutate", "faults"):
        p = sub.add_parser(name); p.add_argument("repo"); p.add_argument("out")
        p.add_argument("--workers", type=int, default=8)
        p.add_argument("--per-file", type=int, default=12); p.add_argument("--seed", type=int, default=1)
        p.add_argument("--max", type=int, default=150)
        p.add_argument("--timeout", type=float, default=60.0, help="seconds per fixture run on a mutant or fault")
        p.add_argument("--head-timeout", type=float, default=300.0, help="seconds per fixture run on the unchanged code")
    a = ap.parse_args()
    if a.workers > 8:
        raise SystemExit("--workers is capped at 8")
    REPO_FOR_PARSER = Path(a.repo).resolve()
    {"reach": cmd_reach, "mutate": cmd_mutate, "faults": cmd_faults}[a.cmd](a)


if __name__ == "__main__":
    main()
