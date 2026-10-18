# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""testprune inputs for a Go module: per-test reach, kill matrix of mutants, reintroduced bug fixes.

Writes the same files as the Python side (reach.json, mut/kills.jsonl, mut/tests.json, flt/faults.jsonl),
so testprune.py rank/evaluate work unchanged. Test ids are "<package dir>::<TestName>".

uv run go_adapter.py reach  <repo> <out_dir> [--workers 16]
uv run go_adapter.py mutate <repo> <out_dir> [--per-file 40] [--seed 1] [--workers 16]
uv run go_adapter.py faults <repo> <out_dir> [--max 120] [--workers 16]
"""
import argparse, json, os, random, re, shutil, subprocess, tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HELPER = Path(__file__).parent / "gohelper/gohelper"
FIX = re.compile(r"\b(fix|fixes|fixed|bug|regression|issue #?\d+)\b", re.I)


def sh(cmd, cwd=None, timeout=1800, inp=None):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout, input=inp)
    return r.returncode, r.stdout, r.stderr


def jl(text):
    return [json.loads(l) for l in text.splitlines() if l.strip().startswith("{")]


def module(repo):
    return sh("go list -m", cwd=repo)[1].strip()


def product_files(repo):
    _, out, _ = sh("git ls-files '*.go'", cwd=repo)
    return [f for f in out.split() if not f.endswith("_test.go") and "/testdata/" not in f and not f.startswith("vendor/")]


def run_json(repo, pkgs, run=None, timeout=900, extra=""):
    """go test -json; returns (passed tests, failed tests, build_failed packages) as sets of ids."""
    sel = f"-run '^({run})$'" if run else ""
    mod = module(repo)
    try:
        rc, out, _ = sh(f"go test -count=1 -json {extra} {sel} {' '.join(pkgs)}", cwd=repo, timeout=timeout)
    except subprocess.TimeoutExpired:
        rc, out = -9, ""
    if rc in (-9, 137) and run:  # killed (memory or time): every selected test counts as failing
        rel = [p[2:] if p.startswith("./") else p for p in pkgs]
        return set(), {f"{r}::{t}" for r in rel for t in run.split("|")}, set(), {}
    passed, failed, broken, secs = set(), set(), set(), {}
    for e in jl(out):
        pkg = e.get("Package", "")
        rel = pkg[len(mod):].lstrip("/") or "."
        t = e.get("Test")
        a = e.get("Action")
        if t and "/" not in t:
            tid = f"{rel}::{t}"
            if a == "pass":
                passed.add(tid); secs[tid] = e.get("Elapsed", 0.0)
            elif a == "fail":
                failed.add(tid); secs[tid] = e.get("Elapsed", 0.0)
        elif not t and a == "fail" and e.get("FailedBuild"):
            broken.add(rel)
        elif not t and a == "output" and "[build failed]" in e.get("Output", ""):
            broken.add(rel)
    return passed, failed, broken, secs


def coverprofile_lines(path, repo, mod):
    lines = defaultdict(set)
    for l in Path(path).read_text().splitlines()[1:]:
        m = re.match(r"(.+):(\d+)\.\d+,(\d+)\.\d+ \d+ (\d+)$", l)
        if not m or m.group(4) == "0":
            continue
        f = m.group(1)
        f = f[len(mod):].lstrip("/") if f.startswith(mod) else f
        for n in range(int(m.group(2)), int(m.group(3)) + 1):
            lines[f].add(n)
    return lines


def cmd_reach(a):
    repo, out = Path(a.repo).resolve(), Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    mod = module(repo)
    passed, failed, broken, secs = run_json(repo, ["./..."], timeout=3600)
    tests = sorted(passed)  # a test that fails on the unchanged code cannot be judged; it is left out
    funcs = {}
    for f in product_files(repo):
        _, o, _ = sh(f"{HELPER} funcs {f}", cwd=repo)
        funcs[f] = [(r["start"], r["end"], r["name"]) for r in jl(o)]
    _, log, _ = sh("git log --no-merges --format=%x00%s --name-only", cwd=repo)
    fixes = defaultdict(int)
    for block in log.split("\x00")[1:]:
        ls = block.strip().splitlines()
        if ls and FIX.search(ls[0]):
            for f in ls[1:]:
                fixes[f.strip()] += 1

    def one(tid):
        pkg, name = tid.split("::")
        with tempfile.NamedTemporaryFile(suffix=".cov", delete=False) as tf:
            prof = tf.name
        sh(f"go test -count=1 -run '^{name}$' -coverpkg={mod}/... -coverprofile={prof} ./{pkg}", cwd=repo, timeout=900)
        lines = coverprofile_lines(prof, repo, mod) if os.path.exists(prof) and os.path.getsize(prof) else {}
        os.unlink(prof)
        syms, ids = set(), []
        for f, ns in lines.items():
            for n in ns:
                ids.append(f"{f}:{n}")
                sym = next((f"{f}:{nm}" for s, e, nm in funcs.get(f, []) if s <= n <= e), None)
                if sym:
                    syms.add(sym)
        return tid, {"symbols": sorted(syms), "lines": len(ids), "line_ids": sorted(ids)}

    with ThreadPoolExecutor(a.workers) as ex:
        R = dict(ex.map(one, tests))
    sources = {}
    for f in sorted({t.split("::")[0] for t in tests}):
        for tf in Path(repo / f).glob("*_test.go"):
            _, o, _ = sh(f"{HELPER} tests {tf}", cwd=repo)
            for r in jl(o):
                sources[f"{f}::{r['name']}"] = r["source"]
    symbols = {f"{f}:{nm}": {"file": f, "bugfixes": fixes.get(f, 0)} for f, fs in funcs.items() for _, _, nm in fs}
    (out / "reach.json").write_text(json.dumps({"pkg": mod, "symbols": symbols, "tests": R,
                                                 "sources": {t: sources.get(t, "") for t in tests}, "seconds": secs,
                                                 "failing_at_head": sorted(failed), "broken_packages": sorted(broken)}))
    print(f"{len(tests)} passing tests ({len(failed)} failing at head left out), {len(symbols)} functions")


def worker_copy(repo):
    d = Path(tempfile.mkdtemp(prefix="gomut-")) / "repo"
    shutil.copytree(repo, d, symlinks=True, ignore=shutil.ignore_patterns(".git"))
    return d


def cmd_mutate(a):
    repo, out = Path(a.repo).resolve(), Path(a.out).resolve()
    (out / "mut").mkdir(parents=True, exist_ok=True)
    R = json.loads((out / "reach.json").read_text())
    covered = defaultdict(lambda: defaultdict(set))  # file -> line -> tests
    for t, v in R["tests"].items():
        for lid in v["line_ids"]:
            f, _, n = lid.rpartition(":")
            covered[f][int(n)].add(t)
    rng = random.Random(a.seed)
    jobs = []
    for f in sorted(covered):
        _, o, _ = sh(f"{HELPER} sites {f}", cwd=repo)
        sites = [s for s in jl(o) if s["line"] in covered[f]]
        rng.shuffle(sites)
        for s in sites[: a.per_file]:
            jobs.append({**s, "file": f, "id": f"{f}:{s['line']}:{s['start']}:{s['op']}", "tests": sorted(covered[f][s["line"]])})
    (out / "mut/tests.json").write_text(json.dumps(sorted(R["tests"])))
    (out / "mut/mutants.json").write_text(json.dumps([{k: v for k, v in j.items() if k != "tests"} for j in jobs]))
    done = set()
    kp = out / "mut/kills.jsonl"
    if kp.exists():  # resume: keep finished mutants
        done = {json.loads(l)["id"] for l in kp.read_text().splitlines() if l.strip()}
    todo = [j for j in jobs if j["id"] not in done]
    print(f"{len(jobs)} mutants on covered lines, {len(done)} already done", flush=True)
    pool = [worker_copy(repo) for _ in range(a.workers)]
    free = list(pool)
    import threading
    lock = threading.Lock()

    def one(job):
        with lock:
            tree = free.pop()
        try:
            p = tree / job["file"]
            orig = p.read_bytes()
            b = orig[: job["start"]] + job["rep"].encode() + orig[job["end"]:]
            p.write_bytes(b)
            try:
                bypkg = defaultdict(list)
                for t in job["tests"]:
                    pk, nm = t.split("::")
                    bypkg[pk].append(nm)
                failed, broken = set(), set()
                for pk, names in bypkg.items():
                    _, fl, br, _ = run_json(tree, [f"./{pk}"], run="|".join(names), timeout=300, extra="-timeout 60s")
                    failed |= fl; broken |= br
            finally:
                p.write_bytes(orig)
        finally:
            with lock:
                free.append(tree)
        if broken and not failed:
            status = "invalid"  # the mutant does not compile
        else:
            status = "killed" if failed else "survived"
        return {k: job[k] for k in ("id", "file", "line", "op", "orig", "rep")} | {"status": status, "failed": sorted(failed)}

    from concurrent.futures import as_completed
    with ThreadPoolExecutor(a.workers) as ex, kp.open("a") as fh:
        for i, fut in enumerate(as_completed([ex.submit(one, j) for j in todo])):
            r = fut.result()
            fh.write(json.dumps(r) + "\n"); fh.flush()
            if i % 100 == 0:
                print(i, r["status"], flush=True)
    for t in pool:
        shutil.rmtree(t.parent, ignore_errors=True)


def cmd_faults(a):
    """Revert each bug-fix commit's product change at HEAD; record which tests then fail."""
    repo, out = Path(a.repo).resolve(), Path(a.out).resolve()
    (out / "flt").mkdir(parents=True, exist_ok=True)
    R = json.loads((out / "reach.json").read_text())
    _, log, _ = sh("git log --no-merges --format=%H%x09%s", cwd=repo)
    jobs = []
    for line in log.splitlines():
        h, _, s = line.partition("\t")
        if not FIX.search(s):
            continue
        _, files, _ = sh(f"git show --name-only --format= {h}", cwd=repo)
        prod = [f for f in files.split() if f.endswith(".go") and not f.endswith("_test.go")]
        if prod:
            jobs.append({"commit": h, "subject": s, "files": prod, "kind": "history"})
        if len(jobs) >= a.max:
            break
    pool = [worker_copy(repo) for _ in range(a.workers)]
    import threading
    lock = threading.Lock()
    free = list(pool)

    def one(job):
        files = " ".join(f"'{f}'" for f in job["files"])
        _, patch, _ = sh(f"git diff {job['commit']} {job['commit']}^ -- {files}", cwd=repo)
        with lock:
            tree = free.pop()
        try:
            saved = {f: (tree / f).read_bytes() for f in job["files"] if (tree / f).exists()}
            code, _, _ = sh("patch -p1 --dry-run -s", cwd=tree, inp=patch)
            if code:
                return {**job, "applies": False}
            sh("patch -p1 -s", cwd=tree, inp=patch)
            try:
                passed, failed, broken, _ = run_json(tree, ["./..."], timeout=900, extra="-timeout 120s")
            finally:
                for f, b in saved.items():
                    (tree / f).write_bytes(b)
                for f in job["files"]:
                    if f not in saved:
                        (tree / f).unlink(missing_ok=True)
                for rej in tree.rglob("*.orig"):
                    rej.unlink()
        finally:
            with lock:
                free.append(tree)
        known = set(R["tests"])
        return {**job, "applies": True, "caught_by": sorted(failed & known), "broken_packages": sorted(broken)}

    with ThreadPoolExecutor(a.workers) as ex, (out / "flt/faults.jsonl").open("w") as fh:
        for r in ex.map(one, jobs):
            fh.write(json.dumps(r) + "\n")
    for t in pool:
        shutil.rmtree(t.parent, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("reach", "mutate", "faults"):
        p = sub.add_parser(name); p.add_argument("repo"); p.add_argument("out")
        p.add_argument("--workers", type=int, default=16)
        p.add_argument("--per-file", type=int, default=40); p.add_argument("--seed", type=int, default=1)
        p.add_argument("--max", type=int, default=120)
    a = ap.parse_args()
    {"reach": cmd_reach, "mutate": cmd_mutate, "faults": cmd_faults}[a.cmd](a)


if __name__ == "__main__":
    main()
