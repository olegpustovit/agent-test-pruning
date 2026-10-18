# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Mutant results clustered by product file: bootstrap over files and a file-level sign test.

Mutants in one file are not independent, so the unit here is the file: per file, the share of its detected mutants
that the kept tests still detect; a method is compared with coverage by the number of files where it keeps more
or fewer, and its mean share by a bootstrap over files (2,000 resamples, weighted by the file's detected mutants).

uv run cluster_stats.py <eval_dir> <method order file stem>... [--budget 10]
"""
import argparse, json, math
from collections import defaultdict
from pathlib import Path

import numpy as np


def sign_test(a, b):
    n = a + b
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, min(a, b) + 1)) / 2 ** n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("eval_dir"); ap.add_argument("methods", nargs="+")
    ap.add_argument("--budget", type=float, default=10.0); ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args()
    d = Path(a.eval_dir)
    byfile = defaultdict(list)
    for k in map(json.loads, open(d / "mut/kills.jsonl")):
        if k["status"] == "killed" and k["failed"]:
            byfile[k["file"]].append(set(k["failed"]))
    files = sorted(byfile)
    w = np.array([len(byfile[f]) for f in files], float)

    def shares(stem):
        p = d / f"{stem}.json"
        o = json.loads(p.read_text())
        keep = set(o["keeps"][str(a.budget)]) if "keeps" in o else set(o["order"][: max(1, round(len(o["order"]) * a.budget / 100))])
        return np.array([sum(1 for s in byfile[f] if s & keep) / len(byfile[f]) for f in files])

    cov = shares("order-coverage")
    rng = np.random.default_rng(1)
    idx = rng.integers(0, len(files), size=(a.boot, len(files)))
    out = {"files": len(files), "budget": a.budget, "rows": {}}
    for stem in ["order-coverage"] + a.methods:
        s = shares(stem)
        boot = (s[idx] * w[idx]).sum(1) / w[idx].sum(1)
        row = {"weighted_share": float((s * w).sum() / w.sum()), "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]}
        if stem != "order-coverage":
            more, less = int((s > cov).sum()), int((s < cov).sum())
            row.update(files_more=more, files_less=less, p_sign_files=sign_test(more, less))
        out["rows"][stem] = row
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
