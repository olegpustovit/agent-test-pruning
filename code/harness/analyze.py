# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Numbers for the paper from one evaluated stream.

  growth   test growth over the replayed commits (agent vs human), redundancy of the agent suite
  graders  how language-model grades relate to measured value (kills, unique kills, faults caught)

uv run analyze.py growth <run_dir> <eval_dir>
uv run analyze.py graders <eval_dir> <grades.jsonl>... [--reference ref.jsonl]
"""
import ast, hashlib, json, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def value(eval_dir: Path):
    """Measured value per test: mutants killed, mutants only it kills, real faults it catches."""
    tests = json.loads((eval_dir / "mut/tests.json").read_text())
    kills = [json.loads(l) for l in open(eval_dir / "mut/kills.jsonl")]
    v = {t: {"kills": 0, "unique": 0, "faults": 0} for t in tests}
    for k in kills:
        if k["status"] != "killed":
            continue
        for t in k["failed"]:
            if t in v:
                v[t]["kills"] += 1
        if len(k["failed"]) == 1 and k["failed"][0] in v:
            v[k["failed"][0]]["unique"] += 1
    fp = eval_dir / "flt/faults.jsonl"
    if fp.exists():
        for f in map(json.loads, open(fp)):
            for t in f.get("caught_by", []):
                if t in v:
                    v[t]["faults"] += 1
    return v


def norm_hash(src: str):
    """Hash of a test body with names and constants abstracted, to find near-duplicates."""
    try:
        tree = ast.parse(src.strip())
    except SyntaxError:
        return None
    for n in ast.walk(tree):
        if isinstance(n, ast.Name):
            n.id = "_"
        elif isinstance(n, ast.Constant):
            n.value = 0
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            n.name = "_"
        elif isinstance(n, ast.arg):
            n.arg = "_"
    return hashlib.sha1(ast.dump(tree).encode()).hexdigest()


def cmd_growth(run: Path, ev: Path):
    steps = [json.loads(l) for l in open(run / "state.jsonl")]
    repo = run / "repo"

    def lines_at(rev, pathspec):
        _, out = subprocess.getstatusoutput(f"git -C {repo} ls-tree -r --name-only {rev} -- {pathspec}")
        n = 0
        for f in out.split():
            if f.endswith(".py"):
                _, src = subprocess.getstatusoutput(f"git -C {repo} show {rev}:{f}")
                n += sum(1 for l in src.splitlines() if l.strip())
        return n
    first, last = steps[0]["bench_head"] + "~1", steps[-1]["bench_head"]
    cfg = json.loads((run / "config.json").read_text())
    pkg = cfg["pkg"]
    human = "tests ':!tests/agent' ':!tests/toml-test'"
    res = {"steps": len(steps),
           "product_lines": [lines_at(first, pkg), lines_at(last, pkg)],
           "human_test_lines": [lines_at(first, human), lines_at(last, human)],
           "agent_test_lines": [0, steps[-1]["agent_lines"]],
           "agent_tests": steps[-1]["agent_tests_passed"],
           "human_tests": [steps[0]["human"]["passed"], steps[-1]["human"]["passed"]],
           "cost_usd": round(sum((s["agent"].get("total_cost_usd") or 0) for s in steps), 2),
           "rolled_back_files": sum(len(s["rolled_back"]) for s in steps),
           "outside_edits_reverted": sum(1 for s in steps if s["outside_reverted"]),
           "curve": [(s["i"], s["agent_lines"], s["agent_tests_passed"], s["human"]["passed"]) for s in steps]}
    v = value(ev)
    R = json.loads((ev / "reach.json").read_text())
    agent = [t for t in v if t.startswith("tests/agent")]
    res["agent_value"] = {
        "tests": len(agent),
        "kill_nothing": sum(1 for t in agent if v[t]["kills"] == 0) / max(len(agent), 1),
        "no_unique_kill": sum(1 for t in agent if v[t]["unique"] == 0) / max(len(agent), 1),
        "catch_a_fault": sum(1 for t in agent if v[t]["faults"] > 0) / max(len(agent), 1)}
    groups = defaultdict(list)
    for t in agent:
        h = norm_hash(R["sources"].get(t, ""))
        if h:
            groups[h].append(t)
    res["agent_value"]["near_duplicate_share"] = sum(len(g) - 1 for g in groups.values() if len(g) > 1) / max(len(agent), 1)
    print(json.dumps(res, indent=1))


def cmd_graders(ev: Path, grade_files, reference=None):
    v = value(ev)
    names = [t for t in v]
    truth_unique = np.array([v[t]["unique"] for t in names], float)
    truth_kills = np.array([v[t]["kills"] for t in names], float)
    out = {}
    ref = None
    if reference:
        ref = {r["test"]: r["grade"] for r in map(json.loads, open(reference)) if isinstance(r.get("grade"), (int, float))}
    for gf in grade_files:
        g = {r["test"]: r["grade"] for r in map(json.loads, open(gf)) if isinstance(r.get("grade"), (int, float))}
        common = [i for i, t in enumerate(names) if t in g]
        gv = np.array([g[names[i]] for i in common], float)
        row = {"n": len(common), "mean_grade": float(gv.mean()) if len(gv) else None,
               "spearman_kills": spearman(gv, truth_kills[common]) if len(common) > 2 else None,
               "spearman_unique": spearman(gv, truth_unique[common]) if len(common) > 2 else None}
        # grade by measured-value band: tests that kill nothing, kill only shared mutants, have unique kills
        bands = {"kills_nothing": truth_kills[common] == 0,
                 "shared_kills_only": (truth_kills[common] > 0) & (truth_unique[common] == 0),
                 "unique_kills": truth_unique[common] > 0}
        row["mean_grade_by_band"] = {k: (float(gv[m].mean()) if m.any() else None) for k, m in bands.items()}
        row["share_graded_4_5_by_band"] = {k: (float((gv[m] >= 4).mean()) if m.any() else None) for k, m in bands.items()}
        if ref:
            both = [t for t in g if t in ref]
            d = np.array([g[t] - ref[t] for t in both], float)
            row["vs_reference"] = {"n": len(both), "bias": float(d.mean()) if len(d) else None,
                                   "spearman": spearman([g[t] for t in both], [ref[t] for t in both]) if len(both) > 2 else None}
            # bias on a sample spread evenly over the reference grades vs on the suite's own mix
            per = defaultdict(list)
            for t in both:
                per[round(ref[t])].append(g[t] - ref[t])
            row["bias_by_reference_grade"] = {k: float(np.mean(x)) for k, x in sorted(per.items())}
            row["bias_even_over_grades"] = float(np.mean([np.mean(x) for x in per.values()])) if per else None
        out[gf] = row
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "growth":
        cmd_growth(Path(sys.argv[2]), Path(sys.argv[3]))
    elif sys.argv[1] == "graders":
        args = sys.argv[2:]
        ref = None
        if "--reference" in args:
            i = args.index("--reference"); ref = args[i + 1]; args = args[:i] + args[i + 2:]
        cmd_graders(Path(args[0]), args[1:], ref)
