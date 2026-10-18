# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Uncertainty for the pruning comparison: bootstrap intervals over mutants (and bugs), paired sign tests.

For each order file in an evaluation folder and each budget, a mutant counts as kept when a kept test detects it.
Random and FAST-R are summarised over their seeds (mean, min, max). Paired tests compare each method with
coverage on the same mutants: methods detecting a mutant coverage misses, and the reverse; exact two-sided sign test.

uv run stats.py <eval_dir> [--budgets 10 20 30] [--boot 2000] > stats.json
"""
import argparse, glob, json, math, re
from collections import defaultdict
from pathlib import Path

import numpy as np


def sign_test(a, b):
    n = a + b
    if n == 0:
        return 1.0
    k = min(a, b)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("eval_dir"); ap.add_argument("--budgets", type=float, nargs="+", default=[10.0, 20.0, 30.0])
    ap.add_argument("--boot", type=int, default=2000); ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    d = Path(a.eval_dir)
    kills = [json.loads(l) for l in open(d / "mut/kills.jsonl")]
    muts = [set(k["failed"]) for k in kills if k["status"] == "killed" and k["failed"]]
    faults = []
    fp = d / "flt/faults.jsonl"
    if fp.exists():
        faults = [set(f["caught_by"]) for f in map(json.loads, open(fp)) if f.get("applies") and f.get("caught_by")]
    orders = {}
    for p in sorted(glob.glob(str(d / "order-*.json"))) + sorted(glob.glob(str(d / "keep-*.json"))):
        name = Path(p).stem.removeprefix("order-").removeprefix("keep-")
        orders[name] = json.loads(Path(p).read_text())
    rng = np.random.default_rng(a.seed)
    out = {"n_mutants": len(muts), "n_bugs": len(faults), "rows": {}}
    for b in a.budgets:
        det = {}  # method -> (mutant vector, bug vector)
        for name, o in orders.items():
            if "keeps" in o:
                if str(b) not in o["keeps"] or not o["keeps"][str(b)]:
                    continue
                keep = set(o["keeps"][str(b)])
            else:
                keep = set(o["order"][: max(1, round(len(o["order"]) * b / 100))])
            det[name] = (np.array([bool(s & keep) for s in muts]), np.array([bool(s & keep) for s in faults]))
        groups = defaultdict(list)
        for name in det:
            groups[re.sub(r"-\d+$", "", name) if re.match(r"(random|fastr)-\d+$", name) else name].append(name)
        idx = rng.integers(0, len(muts), size=(a.boot, len(muts))) if muts else None
        rows = {}
        cov = det.get("coverage")
        for g, names in groups.items():
            mv = np.mean([det[n][0] for n in names], axis=0)
            bv = np.mean([det[n][1] for n in names], axis=0) if faults else np.array([])
            row = {"seeds": len(names), "mutants": float(mv.mean())}
            if len(names) > 1:
                per = [det[n][0].mean() for n in names]
                row["mutants_min"], row["mutants_max"] = float(min(per)), float(max(per))
            if idx is not None:
                bs = mv[idx].mean(axis=1)
                row["mutants_ci95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
            if faults:
                row["bugs"] = float(bv.mean())
            if cov is not None and len(names) == 1 and g != "coverage":
                m = det[names[0]][0]
                row["vs_coverage_mutants"] = {"only_this": int((m & ~cov[0]).sum()), "only_coverage": int((~m & cov[0]).sum()),
                                              "p_sign": sign_test(int((m & ~cov[0]).sum()), int((~m & cov[0]).sum()))}
                if faults:
                    f = det[names[0]][1]
                    row["vs_coverage_bugs"] = {"only_this": int((f & ~cov[1]).sum()), "only_coverage": int((~f & cov[1]).sum()),
                                               "p_sign": sign_test(int((f & ~cov[1]).sum()), int((~f & cov[1]).sum()))}
            rows[g] = row
        out["rows"][str(b)] = rows
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
