# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Time-split evaluation: prune the suite as it was at T with information from before T, score it on bugs fixed after T.

uv run timesplit.py labels  <ci-labels.jsonl> <reach.json at T> <T iso> <out.jsonl>
uv run timesplit.py faults  <clone> <reach.json at T> <T repo worktree> <T iso> <out_dir> [--workers 4]
uv run timesplit.py ciorder <reach.json> <labels.jsonl> <coverage order> <out.json>
uv run timesplit.py stats   --kills K --faults F --coverage C --blend B --random R1 R2 ... [--budgets 10 20 30]

faults: for each fix-like commit F (go_adapter.FIX, touching product .go files) committed after T, the product tree at
F (fixed) and at F^ (buggy) each get the test files of T (every *_test.go and every testdata/ directory replaced by
T's). A T-test catches the bug when it passes on F and fails on F^, twice in a row each (a second run confirms);
a test whose package does not build, or that fails on F, is not counted for that bug. Output flt/faults.jsonl,
kind "after_T", in the go_adapter.py faults format.
"""
import argparse, json, math, random, shutil, subprocess, tempfile, threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from go_adapter import FIX, run_json, sh


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def cmd_labels(a):
    R = json.loads(Path(a.reach).read_text())
    T = ts(a.T)
    kept = n_all = n_before = 0
    with open(a.out, "w") as fh:
        for l in map(json.loads, open(a.labels)):
            n_all += 1
            if ts(l["at"]) >= T:
                continue
            n_before += 1
            if l["test"] in R["tests"]:
                fh.write(json.dumps(l) + "\n"); kept += 1
    print(json.dumps({"labels": n_all, "before_T": n_before, "before_T_on_T_tests": kept}))


def overlay_tests(tree: Path, ttree: Path):
    """Replace every test file and testdata directory of tree by those of the T worktree."""
    for f in list(tree.rglob("*_test.go")):
        if "/testdata/" not in str(f.relative_to(tree)):
            f.unlink()
    for d in sorted(tree.rglob("testdata"), key=lambda p: len(p.parts)):
        if d.is_dir() and d.exists():
            shutil.rmtree(d)
    for f in ttree.rglob("*_test.go"):
        rel = f.relative_to(ttree)
        if ".git" in rel.parts or "testdata" in rel.parts:
            continue
        (tree / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, tree / rel)
    for d in ttree.rglob("testdata"):
        rel = d.relative_to(ttree)
        if d.is_dir() and "testdata" not in rel.parts[:-1] and not (tree / rel).exists():
            (tree / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(d, tree / rel, symlinks=True)


def export(clone, rev, dest: Path):
    dest.mkdir(parents=True)
    code, _, err = sh(f"git -C {clone} archive {rev} | tar -x -C {dest}", timeout=600)
    if code:
        raise RuntimeError(err)


def cmd_faults(a):
    clone, ttree, out = Path(a.clone).resolve(), Path(a.ttree).resolve(), Path(a.out).resolve()
    (out / "flt").mkdir(parents=True, exist_ok=True)
    known = set(json.loads(Path(a.reach).read_text())["tests"])
    T = ts(a.T)
    _, log, _ = sh("git log --no-merges --format=%H%x09%cI%x09%s HEAD", cwd=clone)
    jobs = []
    for line in log.splitlines():
        h, d, s = line.split("\t", 2)
        if ts(d) < T or not FIX.search(s) or (a.only and not any(h.startswith(x) for x in a.only)):
            continue
        _, files, _ = sh(f"git show --name-only --format= {h}", cwd=clone)
        prod = [f for f in files.split() if f.endswith(".go") and not f.endswith("_test.go")]
        if prod:
            jobs.append({"commit": h, "date": d, "subject": s, "files": prod, "kind": "after_T"})
    print(f"{len(jobs)} fix-like commits after {a.T}", flush=True)
    lock = threading.Lock()

    def one(job):
        work = Path(tempfile.mkdtemp(prefix="tsplit-"))
        try:
            fixed, buggy = work / "fixed", work / "buggy"
            export(clone, job["commit"], fixed)
            export(clone, job["commit"] + "^", buggy)
            overlay_tests(fixed, ttree)
            overlay_tests(buggy, ttree)
            pf, ff, bf, _ = run_json(fixed, ["./..."], timeout=1800, extra="-timeout 120s")
            pf &= known
            pb, fb, bb, _ = run_json(buggy, ["./..."], timeout=1800, extra="-timeout 120s")
            cand = sorted(fb & pf)
            caught = []
            if cand:  # confirm: the candidates again, on both trees
                bypkg = {}
                for t in cand:
                    bypkg.setdefault(t.split("::")[0], []).append(t.split("::")[1])
                for pk, names in bypkg.items():
                    sel = "|".join(names)
                    p2, _, _, _ = run_json(fixed, [f"./{pk}"], run=sel, timeout=900, extra="-timeout 120s")
                    _, f2, _, _ = run_json(buggy, [f"./{pk}"], run=sel, timeout=900, extra="-timeout 120s")
                    caught += [f"{pk}::{n}" for n in names if f"{pk}::{n}" in p2 and f"{pk}::{n}" in f2]
            r = {**job, "applies": True, "caught_by": sorted(caught), "n_T_tests_pass_on_fixed": len(pf),
                 "n_T_tests_fail_on_fixed": len(ff & known), "broken_packages_fixed": sorted(bf),
                 "broken_packages_buggy": sorted(bb), "unconfirmed": sorted(set(cand) - set(caught))}
        except Exception as e:  # noqa: BLE001
            r = {**job, "applies": False, "error": str(e)[:500]}
        finally:
            shutil.rmtree(work, ignore_errors=True)
        with lock:
            print(job["commit"][:8], "caught by", len(r.get("caught_by", [])), "pass on F", r.get("n_T_tests_pass_on_fixed"), flush=True)
        return r

    with ThreadPoolExecutor(a.workers) as ex, (out / "flt/faults.jsonl").open("w") as fh:
        for r in ex.map(one, jobs):
            fh.write(json.dumps(r) + "\n"); fh.flush()


def cmd_ciorder(a):
    """CI order without Jev: tests that caught before T first, by number of catches, then the rest in coverage order."""
    R = json.loads(Path(a.reach).read_text())
    cov = json.loads(Path(a.coverage).read_text())["order"]
    pos = {t: i for i, t in enumerate(cov)}
    catches = {}
    for l in map(json.loads, open(a.labels)):
        if l["label"] == "catch" and l["test"] in R["tests"]:
            catches[l["test"]] = catches.get(l["test"], 0) + 1
    past = sorted(catches, key=lambda t: (-catches[t], pos[t]))
    order = past + [t for t in cov if t not in catches]
    Path(a.out).write_text(json.dumps({"method": "ci", "order": order, "n_catching": len(past), "catches": catches}))
    print(json.dumps({"tests": len(order), "catching_tests": len(past)}))


def keep(order, b):
    return set(order[: max(1, round(len(order) * b / 100))])


def sign_p(b, c):
    n, k = b + c, min(b, c)
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def boot(sets, keeps, n=2000, seed=1):
    """Percentile 95% intervals for the caught fraction of each keep-set list (a list is averaged, as for random)."""
    rng = random.Random(seed)
    hit = {name: [[1 if s & k else 0 for s in sets] for k in ks] for name, ks in keeps.items()}
    m = len(sets)
    res = {name: [] for name in keeps}
    for _ in range(n):
        idx = [rng.randrange(m) for _ in range(m)]
        for name, H in hit.items():
            res[name].append(sum(sum(h[i] for i in idx) for h in H) / (m * len(H)))
    out = {}
    for name, H in hit.items():
        v = sorted(res[name])
        out[name] = {"point": sum(map(sum, H)) / (m * len(H)), "lo": v[int(0.025 * n)], "hi": v[int(0.975 * n) - 1]}
    return out


def cmd_stats(a):
    faults = [json.loads(l) for l in open(a.faults)]
    bugs = [set(f["caught_by"]) for f in faults if f.get("applies") and f.get("caught_by")]
    mut = [set(k["failed"]) for k in map(json.loads, open(a.kills)) if k["status"] == "killed" and k["failed"]]
    cov = json.loads(Path(a.coverage).read_text())["order"]
    bl = json.loads(Path(a.blend).read_text())["order"]
    rnd = [json.loads(Path(p).read_text())["order"] for p in a.random]
    out = {"n_bugs_caught_by_full_suite": len(bugs), "n_killed_mutants": len(mut), "budgets": {}}
    for b in a.budgets:
        kc, kb = keep(cov, b), keep(bl, b)
        only_b = sum(1 for s in bugs if s & kb and not s & kc)
        only_c = sum(1 for s in bugs if s & kc and not s & kb)
        mb = sum(1 for s in mut if s & kb and not s & kc)
        mc = sum(1 for s in mut if s & kc and not s & kb)
        keeps = {"coverage": [kc], "blend": [kb], "random_mean": [keep(o, b) for o in rnd]}
        out["budgets"][str(b)] = {
            "bugs_paired": {"blend_not_coverage": only_b, "coverage_not_blend": only_c, "sign_test_p": sign_p(only_b, only_c)},
            "mutants_paired": {"blend_not_coverage": mb, "coverage_not_blend": mc, "sign_test_p": sign_p(mb, mc)},
            "bugs_ci95": boot(bugs, keeps, seed=1) if bugs else None,
            "mutants_ci95": boot(mut, keeps, seed=2) if mut else None}
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("labels"); p.add_argument("labels"); p.add_argument("reach"); p.add_argument("T"); p.add_argument("out")
    p = sub.add_parser("faults"); p.add_argument("clone"); p.add_argument("reach"); p.add_argument("ttree"); p.add_argument("T")
    p.add_argument("out"); p.add_argument("--workers", type=int, default=4); p.add_argument("--only", nargs="*")
    p = sub.add_parser("ciorder"); p.add_argument("reach"); p.add_argument("labels"); p.add_argument("coverage"); p.add_argument("out")
    p = sub.add_parser("stats"); p.add_argument("--kills"); p.add_argument("--faults"); p.add_argument("--coverage"); p.add_argument("--blend")
    p.add_argument("--random", nargs="+"); p.add_argument("--budgets", type=float, nargs="+", default=[10, 20, 30])
    a = ap.parse_args()
    {"labels": cmd_labels, "faults": cmd_faults, "ciorder": cmd_ciorder, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    main()
