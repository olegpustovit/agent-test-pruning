# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "scikit-learn>=1.4", "coverage>=7.4"]
# ///
"""testprune: choose which tests of a pytest suite to keep under a budget.

  reach    per-test coverage (which product functions each test executes) -> reach.json
  rank     order tests by a method -> order.json   (risk, coverage, fastr, random, combined, judge)
  evaluate share of mutants / faults still detected when keeping the top k% of each order

uv run testprune.py reach <repo> <pkg> <tests> <out.json>
uv run testprune.py rank <reach.json> <method> <out.json> [--grades grades.json] [--seed 1] [--no-bugfix]
uv run testprune.py evaluate <orders...> --kills kills.jsonl --faults faults.jsonl --budgets 10 20 30
"""
import argparse, ast, json, math, random, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

import numpy as np

FIX = re.compile(r"\b(fix|fixes|fixed|bug|regression|issue #?\d+)\b", re.I)


def sh(cmd, cwd=None, timeout=3600):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


# ---------- reach ----------

def functions(path: Path):
    """(start, end, qualified name) for every function in a file."""
    tree = ast.parse(path.read_text())
    out = []

    def walk(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{prefix}{ch.name}"
                if not isinstance(ch, ast.ClassDef):
                    out.append((ch.lineno, ch.end_lineno, name))
                walk(ch, name + ".")
    walk(tree, "")
    return out


def bugfix_counts(repo: Path, pkg: str):
    _, out = sh(f"git log --no-merges --format=%x00%s --name-only -- {pkg}", cwd=repo)
    counts = defaultdict(int)
    for block in out.split("\x00")[1:]:
        lines = block.strip().splitlines()
        if lines and FIX.search(lines[0]):
            for f in lines[1:]:
                counts[f.strip()] += 1
    return counts


def cmd_reach(a):
    repo = Path(a.repo).resolve()
    py = repo / ".venv/bin/python"
    sh(f"uv pip install -q --python {py} coverage pytest-cov", cwd=repo)
    sh(f"{py} -m pytest -q -p no:cacheprovider --cov={a.pkg} --cov-context=test --cov-report= --junitxml=.reach-junit.xml {a.tests}", cwd=repo)
    # Read per-test contexts from coverage's own database (the JSON export can be gigabytes).
    from coverage import CoverageData
    data = CoverageData(basename=str(repo / ".coverage"))
    data.read()
    fixes = bugfix_counts(repo, a.pkg)
    tests = defaultdict(lambda: {"symbols": set(), "lines": set()})
    symbols = {}
    for absf in data.measured_files():
        rel = str(Path(absf).resolve().relative_to(repo)) if Path(absf).is_absolute() else absf
        fns = functions(repo / rel)
        for line, ctxs in (data.contexts_by_lineno(absf) or {}).items():
            sym = next((f"{rel}:{n}" for s, e, n in fns if s <= line <= e), None)
            for c in ctxs:
                if not c:
                    continue
                t = c.split("|")[0]
                tests[t]["lines"].add(f"{rel}:{line}")
                if sym:
                    tests[t]["symbols"].add(sym)
        for s, e, n in fns:
            symbols[f"{rel}:{n}"] = {"file": rel, "bugfixes": fixes.get(rel, 0)}
    _, src_out = sh(f"{py} -m pytest -q -p no:cacheprovider --collect-only {a.tests}", cwd=repo)
    collected = [l.strip() for l in src_out.splitlines() if "::" in l]
    out = {"pkg": a.pkg, "symbols": symbols,
           "tests": {t: {"symbols": sorted(tests[t]["symbols"]) if t in tests else [],
                         "lines": len(tests[t]["lines"]) if t in tests else 0,
                         "line_ids": sorted(tests[t]["lines"]) if t in tests else []} for t in collected},
           "sources": test_sources(repo, collected), "seconds": durations(repo / ".reach-junit.xml")}
    Path(a.out).write_text(json.dumps(out))
    print(f"{len(collected)} tests, {len(symbols)} symbols", file=sys.stderr)


def durations(xml: Path):
    """Seconds per test from pytest's junit report, keyed by node id."""
    import xml.etree.ElementTree as ET
    out = {}
    if not xml.exists():
        return out
    for tc in ET.parse(xml).iter("testcase"):
        cls, name = tc.get("classname", ""), tc.get("name", "")
        parts = cls.split(".")
        # classname is the dotted module path plus any class; rebuild the node id
        for k in range(len(parts), 0, -1):
            f = "/".join(parts[:k]) + ".py"
            if (xml.parent / f).exists():
                node = "::".join([f] + parts[k:] + [name])
                out[node] = float(tc.get("time", 0))
                break
    return out


def test_sources(repo: Path, nodes):
    """Source text of each test function (for FAST-R and graders)."""
    out, cache = {}, {}
    for n in nodes:
        f, _, rest = n.partition("::")
        name = rest.split("::")[-1].split("[")[0]
        if f not in cache:
            try:
                src = (repo / f).read_text()
                cache[f] = (src, ast.parse(src))
            except Exception:
                cache[f] = ("", None)
        src, tree = cache[f]
        seg = ""
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                    seg = ast.get_source_segment(src, node) or ""
                    break
        out[n] = seg
    return out


# ---------- rank ----------

TIERS = []  # (compiled path regex, weight), first match wins; set from --tiers


def tier_weight(path):
    for rx, w in TIERS:
        if rx.search(path):
            return w
    return 1.0


def risk_weight(sym, use_bugfix=True):
    """tier weight x (0.5 + ln(1 + bug-fix commits on the symbol's file))."""
    return tier_weight(sym["file"]) * ((0.5 + math.log1p(sym["bugfixes"])) if use_bugfix else 1.0)


def greedy(tests, gain_of, value=None):
    """Greedy selection by marginal gain; a symbol's weight halves each time a picked test reaches it."""
    hits = defaultdict(int)
    left = set(tests)
    order = []
    while left:
        best = max(left, key=lambda t: (gain_of(t, hits) * (value(t) if value else 1.0), t))
        order.append(best)
        left.remove(best)
        for s in tests[best]:
            hits[s] += 1
    return order


def rank_risk(R, use_bugfix=True, quality=None, exponent=4.0):
    syms = R["symbols"]
    tests = {t: v["symbols"] for t, v in R["tests"].items()}
    w = {s: risk_weight(v, use_bugfix) for s, v in syms.items()}
    gain = lambda t, hits: sum(w.get(s, 0) * 0.5 ** hits[s] for s in tests[t])
    value = (lambda t: max(quality.get(t, 0.0), 1e-3) ** exponent) if quality else None
    return greedy(tests, gain, value)


def rank_coverage(R):
    """Additional-coverage greedy (classic minimization): maximize newly covered lines."""
    tests = {t: set(v["line_ids"]) for t, v in R["tests"].items()}
    covered, left, order = set(), set(tests), []
    while left:
        best = max(left, key=lambda t: (len(tests[t] - covered), len(tests[t]), t))
        order.append(best)
        left.remove(best)
        covered |= tests[best]
    return order


def rank_fastr(R, seed=1, dims=64):
    """FAST-R style (Cruciani et al. 2019): random-projected bag of tokens, farthest-first traversal."""
    rng = np.random.default_rng(seed)
    names = sorted(R["tests"])
    toks = [re.findall(r"[A-Za-z_]+|\d+|\S", R["sources"].get(n, "")) for n in names]
    vocab = {t: i for i, t in enumerate(sorted({t for ts in toks for t in ts}))}
    proj = rng.standard_normal((max(len(vocab), 1), dims)) / math.sqrt(dims)
    X = np.zeros((len(names), dims))
    for i, ts in enumerate(toks):
        for t in ts:
            X[i] += proj[vocab[t]]
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    first = int(rng.integers(len(names)))
    order, dist = [first], 1 - X @ X[first]
    dist[first] = -1
    for _ in range(len(names) - 1):
        j = int(np.argmax(dist))
        order.append(j)
        dist = np.minimum(dist, 1 - X @ X[j])
        dist[order] = -1
    return [names[i] for i in order]


def load_grades(path):
    text = Path(path).read_text()
    if text.lstrip().startswith("{") and "\n{" not in text.strip():
        return json.loads(text)
    out = {}
    for line in text.splitlines():
        r = json.loads(line)
        if isinstance(r.get("grade"), (int, float)):
            out[r["test"]] = r["grade"]
    return out


def cmd_rank(a):
    if a.tiers:
        TIERS[:] = [(re.compile(r["match"]), float(r["weight"])) for r in json.loads(Path(a.tiers).read_text())]
    R = json.loads(Path(a.reach).read_text())
    grades = load_grades(a.grades) if a.grades else None
    if a.method == "random":
        order = sorted(R["tests"])
        random.Random(a.seed).shuffle(order)
    elif a.method == "risk":
        order = rank_risk(R, use_bugfix=not a.no_bugfix)
    elif a.method == "coverage":
        order = rank_coverage(R)
    elif a.method == "fastr":
        order = rank_fastr(R, seed=a.seed)
    elif a.method == "judge":  # keep the highest-graded tests; ties broken at random
        rng = random.Random(a.seed)
        order = sorted(R["tests"], key=lambda t: (-grades.get(t, 0), rng.random()))
    elif a.method == "combined":  # risk gain x q^4; q from the quality score (0-1) or a grade mapped to 0-1
        q = json.loads(Path(a.quality).read_text()) if a.quality else {t: (g - 1) / 4 for t, g in grades.items()}
        order = rank_risk(R, use_bugfix=not a.no_bugfix, quality=q)
    else:
        raise SystemExit(f"unknown method {a.method}")
    Path(a.out).write_text(json.dumps({"method": a.method, "seed": a.seed, "no_bugfix": a.no_bugfix, "order": order}))


# ---------- grade ----------

GRADE_PROMPT = """You are grading the tests of a software project. Rubric:

{rubric}

For each test below, reply with a JSON array, one object per test, in the same order:
{{"id": <id>, "grade": 1-5, "assertions": ..., "exercises": ..., "expected_from": ..., "error_path": ...}}
Reply with the JSON array only.

{tests}
"""


def cmd_grade(a):
    R = json.loads(Path(a.reach).read_text())
    rubric = (Path(__file__).parent / "rubric.md").read_text()
    names = json.loads(Path(a.sample).read_text()) if a.sample else sorted(R["tests"])
    out_path = Path(a.out)
    done = {}
    if out_path.exists():
        done = {r["test"]: r for r in map(json.loads, out_path.read_text().splitlines())}
    todo = [n for n in names if n not in done]
    with out_path.open("a") as fh:
        for i in range(0, len(todo), a.batch):
            chunk = todo[i:i + a.batch]
            body = "\n\n".join(f"### id {j}: {n}\nReaches: {', '.join(R['tests'][n]['symbols'][:12]) or 'nothing in the package'}\n```\n{R['sources'].get(n, '')[:4000]}\n```"
                               for j, n in enumerate(chunk))
            prompt = GRADE_PROMPT.format(rubric=rubric, tests=body)
            r = subprocess.run(["claude", "-p", prompt, "--model", a.model, "--output-format", "json",
                                "--no-session-persistence", "--tools", ""], capture_output=True, text=True, timeout=900)
            try:
                meta = json.loads(r.stdout)
                text = meta.get("result", "")
            except Exception as exc:
                print(f"batch {i}: no reply ({exc})", file=sys.stderr)
                continue
            try:
                arr = json.loads(text[text.index("["): text.rindex("]") + 1])
            except Exception:
                # fall back to the fields that matter, one object at a time
                arr = []
                for m in re.finditer(r"\{[^{}]*?\"id\"\s*:\s*(\d+)[^{}]*?\}", text, re.S):
                    obj = {"id": int(m.group(1))}
                    for k in ("grade",):
                        g = re.search(rf'"{k}"\s*:\s*"?(\d)', m.group(0))
                        if g:
                            obj[k] = int(g.group(1))
                    for k in ("assertions", "exercises", "expected_from", "error_path"):
                        g = re.search(rf'"{k}"\s*:\s*"([a-z_]+)"', m.group(0))
                        if g:
                            obj[k] = g.group(1)
                    arr.append(obj)
                if not arr:
                    print(f"batch {i}: unparsed", file=sys.stderr)
                    continue
            for obj in arr:
                j = obj.get("id")
                if isinstance(j, int) and 0 <= j < len(chunk):
                    fh.write(json.dumps({"test": chunk[j], "model": a.model, **{k: v for k, v in obj.items() if k != "id"},
                                         "cost_usd": meta.get("total_cost_usd", 0) / len(chunk)}) + "\n")
            fh.flush()


# ---------- quality score ----------

FACETS = json.loads((Path(__file__).parent / "jev_facets.json").read_text())
TYPED = {f["name"]: list(f["options"]) for f in FACETS["facets"]}  # oracle, subject, real_code, risk_area


def features(R, typed):
    """The method's quality features: Jev facet answers (one-hot and option weight), parser counts, reach."""
    names = sorted(R["tests"])
    rows = []
    for n in names:
        src = R["sources"].get(n, "")
        t = typed.get(n, {})
        f = [len(src.splitlines()), src.count("assert") + len(re.findall(r"\.(Error|Errorf|Fatal|Fatalf)\(", src)),
             len(re.findall(r"mock|patch|Mock|fake|Fake|stub|monkeypatch", src)),
             len(R["tests"][n]["symbols"]), math.log1p(R["tests"][n]["lines"])]
        for q, vals in TYPED.items():
            f += [1.0 if t.get(q) == v else 0.0 for v in vals]
            if q in FACETS["weights"]:
                f.append(FACETS["weights"][q].get(t.get(q), 0.0))
        rows.append(f)
    X = np.array(rows, dtype=float)
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    return names, np.hstack([X, np.ones((len(names), 1))])


def ridge(X, y, lam=1.0):
    return np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ y)


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def cmd_quality(a):
    """Fit the quality score on reference grades of a sample; report out-of-fold Spearman; write q in 0-1."""
    R = json.loads(Path(a.reach).read_text())
    typed = {r["test"]: r for r in map(json.loads, Path(a.typed).read_text().splitlines())}
    ref = load_grades(a.reference)
    names, X = features(R, typed)
    idx = {n: i for i, n in enumerate(names)}
    lab = [n for n in names if n in ref]
    Xl, yl = X[[idx[n] for n in lab]], np.array([ref[n] for n in lab], dtype=float)
    rng = np.random.default_rng(a.seed)
    folds = rng.integers(0, 5, len(lab))
    oof = np.zeros(len(lab))
    for k in range(5):
        tr, te = folds != k, folds == k
        oof[te] = Xl[te] @ ridge(Xl[tr], yl[tr], a.lam)
    w = ridge(Xl, yl, a.lam)
    pred = X @ w
    q = {n: float(min(max((pred[idx[n]] - 1) / 4, 0.0), 1.0)) for n in names}
    for j, n in enumerate(lab):  # graded tests keep their out-of-fold prediction, so no test is scored by a fit that saw it
        q[n] = float(min(max((oof[j] - 1) / 4, 0.0), 1.0))
    Path(a.out).write_text(json.dumps(q))
    print(json.dumps({"n_labelled": len(lab), "oof_spearman": spearman(oof, yl)}))


# ---------- reading loop with calibration gate ----------

READ_PROMPT = """You are reviewing one test of this repository to decide whether it is worth keeping.
Open the test and the product code it exercises, and read them. Rubric:

{rubric}

Test: {test}
Reply with one JSON object only: {{"grade": 1-5, "reason": "<one sentence>"}}
"""


def read_one(repo, test, model, rubric):
    prompt = READ_PROMPT.format(rubric=rubric, test=test)
    r = subprocess.run(["claude", "-p", prompt, "--model", model, "--output-format", "json", "--no-session-persistence",
                        "--allowedTools", "Read,Grep,Glob", "--disallowedTools", "Edit,Write,Bash"],
                       cwd=repo, capture_output=True, text=True, timeout=900)
    meta = json.loads(r.stdout)
    text = meta.get("result", "")
    obj = json.loads(text[text.index("{"): text.rindex("}") + 1])
    return {"test": test, "grade": obj.get("grade"), "reason": obj.get("reason"), "model": model,
            "cost_usd": meta.get("total_cost_usd")}


def gate_sample(ref, per_grade=8, seed=1):
    rng = random.Random(seed)
    out = []
    for g in range(1, 6):
        pool = sorted(t for t, v in ref.items() if round(v) == g)
        rng.shuffle(pool)
        out += pool[:per_grade]
    return out


def gate_verdict(loop, ref, tests):
    a = np.array([loop[t] for t in tests if t in loop], dtype=float)
    b = np.array([ref[t] for t in tests if t in loop], dtype=float)
    res = {"n": len(a), "spearman": spearman(a, b), "within_one": float(np.mean(np.abs(a - b) <= 1)),
           "bias": float(np.mean(a - b))}
    res["passed"] = res["spearman"] >= 0.6 and res["within_one"] >= 0.8 and abs(res["bias"]) <= 0.5
    return res


def cmd_read(a):
    """Gate the reading loop on reference-graded tests (eight per grade), then read tests in queue order."""
    from concurrent.futures import ThreadPoolExecutor
    rubric = (Path(__file__).parent / "rubric.md").read_text()
    ref = load_grades(a.reference)
    out_path = Path(a.out)
    done = {r["test"]: r for r in map(json.loads, out_path.read_text().splitlines())} if out_path.exists() else {}
    gate = gate_sample(ref, seed=a.seed)
    queue = gate + [t for t in json.loads(Path(a.order).read_text())["order"][: a.n] if t not in gate]
    todo = [t for t in queue if t not in done]
    with out_path.open("a") as fh, ThreadPoolExecutor(a.workers) as ex:
        for r in ex.map(lambda t: _safe(read_one, a.repo, t, a.model, rubric), todo):
            if r:
                fh.write(json.dumps(r) + "\n"); fh.flush()
                done[r["test"]] = r
    loop = {t: r["grade"] for t, r in done.items() if isinstance(r.get("grade"), (int, float))}
    verdict = gate_verdict(loop, ref, gate)
    Path(a.out + ".gate.json").write_text(json.dumps(verdict, indent=1))
    print(json.dumps(verdict))


def _safe(fn, *args):
    try:
        return fn(*args)
    except Exception as exc:
        print(f"read failed: {exc}", file=sys.stderr)
        return None


# ---------- final selection and the ask-the-agent baseline ----------

def cmd_select(a):
    """Keep sets per budget: read tests graded 5, then 4, in combined order; fill with the combined order."""
    order = json.loads(Path(a.order).read_text())["order"]
    read = load_grades(a.read)
    keeps = {}
    for b in a.budgets:
        k = max(1, round(len(order) * b / 100))
        picked = [t for t in order if read.get(t) == 5] + [t for t in order if read.get(t) == 4]
        rest = [t for t in order if t not in set(picked) and read.get(t, 3) >= 3]
        keeps[str(b)] = (picked + rest)[:k]
    Path(a.out).write_text(json.dumps({"method": "testprune", "keeps": keeps}))


ASK_PROMPT = """The test suite under {tests} has grown too large. It has {n} tests. Decide which {k} tests to keep
so that the kept tests still catch as many real bugs in the product code as possible; the others will be deleted.
You may read any file. Do not edit anything. Reply with a JSON array of the pytest node ids to keep, and nothing else.
The node ids are:
{ids}
"""


def extract_ids(text, valid):
    """Node ids from an agent reply, tolerantly: every JSON array in the text is tried (ids themselves
    contain brackets), the longest list of strings wins; failing that, every quoted string. Each string is
    matched exactly, then with escapes undone (a JSON "\\n" read as a newline), then by a unique suffix
    after '::' or '/'. Order is kept, duplicates dropped."""
    dec, best = json.JSONDecoder(), []
    for i, ch in enumerate(text):
        if ch != "[":
            continue
        try:
            v, _ = dec.raw_decode(text, i)
        except ValueError:
            continue
        if isinstance(v, list) and len(v) > len(best) and all(isinstance(x, str) for x in v):
            best = v
    if not best:
        best = re.findall(r'"((?:[^"\\]|\\.)+)"', text) or re.findall(r"^\s*[-*]?\s*`?([\w./\[\]-]+::\S+?)`?\s*$", text, re.M)
    norm = {}
    for t in valid:
        norm.setdefault(t.strip(), t)
        norm.setdefault(t.replace("\\n", "\n").replace("\\t", "\t").strip(), t)
    tails = defaultdict(list)
    for t in valid:
        for sep in ("::", "/"):
            if sep in t:
                tails[t.split(sep, 1)[1]].append(t)
    out, seen = [], set()
    for x in best:
        x = x.strip().strip("`")
        t = norm.get(x) or (tails[x][0] if len(tails.get(x, [])) == 1 else None)
        if t and t not in seen:
            seen.add(t); out.append(t)
    return out, len(best)


def cmd_ask(a):
    R = json.loads(Path(a.reach).read_text())
    names = sorted(R["tests"])
    keeps, info = {}, {}
    for b in a.budgets:
        k = max(1, round(len(names) * b / 100))
        prompt = ASK_PROMPT.format(tests=a.tests, n=len(names), k=k, ids="\n".join(names))
        rec = {"asked": k, "attempts": [], "cost_usd": 0.0}
        for attempt in range(1, a.attempts + 1):
            try:
                r = subprocess.run(["claude", "-p", prompt, "--model", a.model, "--output-format", "json", "--no-session-persistence",
                                    "--allowedTools", "Read,Grep,Glob", "--disallowedTools", "Edit,Write,Bash"],
                                   cwd=a.repo, capture_output=True, text=True, timeout=3600, stdin=subprocess.DEVNULL)
                meta = json.loads(r.stdout)
            except Exception as exc:
                rec["attempts"].append({"error": str(exc)[:300]})
                continue
            text = meta.get("result") or ""
            ids, returned = extract_ids(text, R["tests"])
            rec["cost_usd"] += meta.get("total_cost_usd") or 0.0
            rec["attempts"].append({"returned": returned, "valid": len(ids), "is_error": meta.get("is_error"),
                                    "cost_usd": meta.get("total_cost_usd"), "tail": text[-300:] if not ids else None})
            print(b, "attempt", attempt, "returned", returned, "valid", len(ids), "of", k, meta.get("total_cost_usd"), file=sys.stderr)
            if ids:
                keeps[str(b)] = ids[:k]
                rec.update({"returned": returned, "valid": len(ids), "kept": len(keeps[str(b)])})
                break
        else:
            keeps[str(b)] = []
            rec.update({"returned": 0, "valid": 0, "kept": 0, "failed": True})
        info[str(b)] = rec
    Path(a.out).write_text(json.dumps({"method": "ask-agent", "model": a.model, "keeps": keeps, "info": info}))


# ---------- CI order and the method's combined order ----------

def cmd_ciorder(a):
    """CI order: tests that caught before come first (by number of catches), then P(catch) x q^0.5.
    P(catch) is a gradient-boosted classifier over the test's file and package catch history, Jev facets and size,
    predicted out-of-fold so no test is scored by a model that saw its own label."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.model_selection import cross_val_predict, StratifiedKFold
    R = json.loads(Path(a.reach).read_text())
    q = json.loads(Path(a.quality).read_text())
    typed = {r["test"]: r for r in map(json.loads, Path(a.typed).read_text().splitlines())}
    labels = [json.loads(l) for l in Path(a.labels).read_text().splitlines()]
    catches = defaultdict(int)
    for l in labels:
        if l["label"] == "catch" and l["test"] in R["tests"]:
            catches[l["test"]] += 1
    by_file, by_pkg = defaultdict(int), defaultdict(int)
    for t, n in catches.items():
        by_pkg[t.split("::")[0]] += n
    names, Xq = features(R, typed)
    X = np.array([[by_pkg[t.split("::")[0]] - catches[t]] for t in names], dtype=float)
    X = np.hstack([X, Xq])
    y = np.array([1 if catches[t] else 0 for t in names])
    p = np.zeros(len(names))
    if y.sum() >= 5:
        clf = HistGradientBoostingClassifier(max_iter=300, max_depth=3, class_weight="balanced", random_state=a.seed)
        p = cross_val_predict(clf, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=a.seed), method="predict_proba")[:, 1]
    score = {t: p[i] * max(q.get(t, 0.0), 1e-3) ** 0.5 for i, t in enumerate(names)}
    past = sorted([t for t in names if catches[t]], key=lambda t: (-catches[t], -score[t]))
    rest = sorted([t for t in names if not catches[t]], key=lambda t: -score[t])
    Path(a.out).write_text(json.dumps({"method": "ci", "order": past + rest, "n_catching": int(y.sum())}))
    print(json.dumps({"tests": len(names), "catching_tests": int(y.sum())}))


def cmd_blend(a):
    """The method's order: slots interleaved, 85% from the risk x q^4 order and 15% from the CI order
    (a test already placed is skipped); tests Jev marks as protected are moved to the front as a floor."""
    risk = json.loads(Path(a.risk).read_text())["order"]
    ci = json.loads(Path(a.ci).read_text())["order"]
    # Interleave: slot k goes to the CI order when the CI share of the slots so far falls below ci_share
    # (an even spread, e.g. about every 7th slot for 15%), skipping tests already placed.
    out, seen, i, j, taken_ci = [], set(), 0, 0, 0
    while len(out) < len(risk):
        want_ci = a.ci_share > 0 and taken_ci < a.ci_share * (len(out) + 1)
        src, idx = (ci, j) if want_ci else (risk, i)
        while idx < len(src) and src[idx] in seen:
            idx += 1
        if idx >= len(src):  # this order is used up: take from the other
            src, idx = (risk, i) if want_ci else (ci, j)
            want_ci = not want_ci
            while idx < len(src) and src[idx] in seen:
                idx += 1
            if idx >= len(src):
                break
        out.append(src[idx]); seen.add(src[idx])
        if want_ci:
            j, taken_ci = idx + 1, taken_ci + 1
        else:
            i = idx + 1
    if a.typed:
        prot = {json.loads(l)["test"] for l in Path(a.typed).read_text().splitlines() if json.loads(l).get("risk_area") == "protected"}
        out = [t for t in out if t in prot] + [t for t in out if t not in prot] if a.protected_floor else out
    Path(a.out).write_text(json.dumps({"method": a.name, "order": out}))


# ---------- evaluate ----------

def cmd_evaluate(a):
    kills = [json.loads(l) for l in open(a.kills)] if a.kills else []
    faults = [json.loads(l) for l in open(a.faults)] if a.faults else []
    killed = [set(k["failed"]) for k in kills if k["status"] == "killed" and k["failed"]]
    caught = defaultdict(list)
    for f in faults:
        if f.get("applies") and f.get("caught_by"):
            caught[f["kind"]].append(set(f["caught_by"]))
    secs = json.loads(Path(a.reach).read_text()).get("seconds", {}) if a.reach else {}
    total = sum(secs.values()) or 1.0
    rows = []
    for path in a.orders:
        o = json.loads(Path(path).read_text())
        for b in a.budgets:
            if "keeps" in o:
                if str(b) not in o["keeps"]:
                    continue
                keep = set(o["keeps"][str(b)])
            else:
                keep = set(o["order"][: max(1, round(len(o["order"]) * b / 100))])
            row = {"method": Path(path).stem.removeprefix("order-").removeprefix("keep-"), "seed": o.get("seed"), "no_bugfix": o.get("no_bugfix"), "budget": b,
                   "kept": len(keep), "runtime_kept": sum(secs.get(t, 0) for t in keep) / total,
                   "mutants": sum(1 for s in killed if s & keep) / max(len(killed), 1)}
            for kind, sets in caught.items():
                row[f"faults_{kind}"] = sum(1 for s in sets if s & keep) / max(len(sets), 1)
            rows.append(row)
    print(json.dumps({"n_killed_mutants": len(killed), "n_caught_faults": {k: len(v) for k, v in caught.items()},
                      "rows": rows}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("reach"); p.add_argument("repo"); p.add_argument("pkg"); p.add_argument("tests"); p.add_argument("out")
    p = sub.add_parser("rank"); p.add_argument("reach"); p.add_argument("method"); p.add_argument("out")
    p.add_argument("--grades"); p.add_argument("--quality"); p.add_argument("--tiers"); p.add_argument("--seed", type=int, default=1); p.add_argument("--no-bugfix", action="store_true")
    p = sub.add_parser("quality"); p.add_argument("reach"); p.add_argument("typed"); p.add_argument("reference"); p.add_argument("out")
    p.add_argument("--lam", type=float, default=1.0); p.add_argument("--seed", type=int, default=1)
    p = sub.add_parser("read"); p.add_argument("repo"); p.add_argument("order"); p.add_argument("reference"); p.add_argument("out")
    p.add_argument("--n", type=int, default=300); p.add_argument("--model", default="claude-sonnet-5-5")
    p.add_argument("--workers", type=int, default=4); p.add_argument("--seed", type=int, default=1)
    p = sub.add_parser("select"); p.add_argument("order"); p.add_argument("read"); p.add_argument("out")
    p.add_argument("--budgets", type=float, nargs="+", default=[10, 20, 30])
    p = sub.add_parser("ask"); p.add_argument("repo"); p.add_argument("reach"); p.add_argument("out")
    p.add_argument("--tests", default="tests/agent"); p.add_argument("--model", default="claude-sonnet-5-5")
    p.add_argument("--budgets", type=float, nargs="+", default=[10, 20, 30]); p.add_argument("--attempts", type=int, default=3)
    p = sub.add_parser("grade"); p.add_argument("reach"); p.add_argument("out"); p.add_argument("--sample")
    p.add_argument("--model", default="claude-sonnet-5-5"); p.add_argument("--batch", type=int, default=10)
    p = sub.add_parser("ciorder"); p.add_argument("reach"); p.add_argument("labels"); p.add_argument("typed"); p.add_argument("quality"); p.add_argument("out")
    p.add_argument("--seed", type=int, default=1)
    p = sub.add_parser("blend"); p.add_argument("risk"); p.add_argument("ci"); p.add_argument("out")
    p.add_argument("--ci-share", type=float, default=0.15); p.add_argument("--typed"); p.add_argument("--protected-floor", action="store_true")
    p.add_argument("--name", default="method")
    p = sub.add_parser("evaluate"); p.add_argument("orders", nargs="+"); p.add_argument("--kills"); p.add_argument("--faults"); p.add_argument("--reach")
    p.add_argument("--budgets", type=float, nargs="+", default=[10, 20, 30])
    a = ap.parse_args()
    {"reach": cmd_reach, "rank": cmd_rank, "grade": cmd_grade, "quality": cmd_quality, "read": cmd_read,
     "select": cmd_select, "ask": cmd_ask, "ciorder": cmd_ciorder, "blend": cmd_blend, "evaluate": cmd_evaluate}[a.cmd](a)


if __name__ == "__main__":
    main()
