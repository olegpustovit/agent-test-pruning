# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Kill matrix of a test suite: which tests fail on which mutant.

Mutants are made in function bodies of product files, on lines the suite covers, with eight operators
(comparison flip, and/or swap, removal of not, arithmetic swap, boolean flip, numeric constant +1,
return value to None, raise to pass); at most --per-file per file, drawn with a fixed seed. Each mutant
is written into a private copy of the repository, so workers never share a tree.

uv run mutate.py <repo> <pkg> <out_dir> --tests tests/agent [--workers 16] [--per-file 150] [--seed 1]
"""
import argparse, ast, json, os, random, re, shutil, subprocess, tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

CMP_FLIP = {ast.Lt: ast.GtE, ast.GtE: ast.Lt, ast.Gt: ast.LtE, ast.LtE: ast.Gt, ast.Eq: ast.NotEq,
            ast.NotEq: ast.Eq, ast.Is: ast.IsNot, ast.IsNot: ast.Is, ast.In: ast.NotIn, ast.NotIn: ast.In}
ARITH = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div, ast.Div: ast.Mult, ast.FloorDiv: ast.Mult, ast.Mod: ast.FloorDiv}


def sh(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def mutations(node):
    """Yield (operator, replacement source) for one node."""
    if isinstance(node, ast.Compare) and len(node.ops) == 1 and type(node.ops[0]) in CMP_FLIP:
        n = ast.Compare(node.left, [CMP_FLIP[type(node.ops[0])]()], node.comparators)
        yield "cmp_flip", f"({ast.unparse(n)})"
    elif isinstance(node, ast.BoolOp):
        op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        yield "andor_swap", f"({ast.unparse(ast.BoolOp(op, node.values))})"
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        yield "not_removal", f"({ast.unparse(node.operand)})"
    elif isinstance(node, ast.BinOp) and type(node.op) in ARITH:
        yield "arith_swap", f"({ast.unparse(ast.BinOp(node.left, ARITH[type(node.op)](), node.right))})"
    elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
        yield "bool_flip", repr(not node.value)
    elif isinstance(node, ast.Constant) and type(node.value) in (int, float):
        yield "const_plus1", repr(node.value + 1)
    elif isinstance(node, ast.Return) and node.value is not None and not (
            isinstance(node.value, ast.Constant) and node.value.value is None):
        yield "return_none", "return None"
    elif isinstance(node, ast.Raise):
        yield "raise_pass", "pass"


def candidates(path: Path, covered: set[int]):
    src = path.read_text()
    tree = ast.parse(src)
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for stmt in fn.body:
            for node in ast.walk(stmt):
                if not hasattr(node, "lineno") or node.lineno not in covered or node.lineno != getattr(node, "end_lineno", -1):
                    continue  # single-line nodes on covered lines only
                for op, rep in mutations(node):
                    out.append({"line": node.lineno, "col": node.col_offset, "end_col": node.end_col_offset,
                                "op": op, "rep": rep, "orig": ast.get_source_segment(src, node)})
    # f-strings: drop mutants inside them (their offsets are unreliable on older Pythons)
    fstr = {(n.lineno) for n in ast.walk(tree) if isinstance(n, ast.JoinedStr)}
    uniq = {(m["line"], m["col"], m["end_col"], m["op"]): m for m in out if m["line"] not in fstr}
    return list(uniq.values())


def apply(src: str, m) -> str | None:
    lines = src.splitlines(keepends=True)
    line = lines[m["line"] - 1]
    b = line.encode()
    new = (b[:m["col"]].decode() + m["rep"] + b[m["end_col"]:].decode())
    out = "".join(lines[:m["line"] - 1] + [new] + lines[m["line"]:])
    try:
        ast.parse(out)
    except SyntaxError:
        return None
    return out


def coverage_lines(repo: Path, pkg: str, tests: str):
    py = repo / ".venv/bin/python"
    sh(f"uv pip install -q --python {py} coverage", cwd=repo)
    sh(f"{py} -m coverage run --source={pkg} -m pytest -q -p no:cacheprovider {tests}", cwd=repo, timeout=1800)
    sh(f"{py} -m coverage json -o .cov.json", cwd=repo)
    data = json.loads((repo / ".cov.json").read_text())["files"]
    return {f: set(v["executed_lines"]) for f, v in data.items()}


def collect(repo: Path, tests: str):
    py = repo / ".venv/bin/python"
    _, out = sh(f"{py} -m pytest -q -p no:cacheprovider --collect-only {tests}", cwd=repo)
    return [l.strip() for l in out.splitlines() if "::" in l]


WORK = {}


def init_worker(repo, tests):
    d = Path(tempfile.mkdtemp(prefix="mut-"))
    tree = d / "repo"
    shutil.copytree(repo, tree, symlinks=True, ignore=shutil.ignore_patterns(".git"))
    # the copied venv still points its editable install at the original tree: repoint it
    py = tree / ".venv/bin/python"
    site = tree / ".venv"
    for f in list(site.rglob("*.pth")) + list(site.rglob("__editable__*.py")):
        f.write_text(f.read_text().replace(str(repo), str(tree)))
    WORK.update(tree=tree, py=py, tests=tests, repo=repo)


def run_mutant(job):
    tree, py, tests = WORK["tree"], WORK["py"], WORK["tests"]
    f = tree / job["file"]
    orig = f.read_text()
    f.write_text(job["src"])
    try:
        code, out = sh(f"timeout 300 {py} -m pytest -q -p no:cacheprovider --tb=no -rfE {tests}", cwd=tree, timeout=400)
    finally:
        f.write_text(orig)
    failed = sorted({m.group(1) for m in re.finditer(r"^(?:FAILED|ERROR) (\S+)", out, re.M)})
    status = "timeout" if code == 124 else ("killed" if failed or code not in (0, 5) else "survived")
    return {k: job[k] for k in ("id", "file", "line", "op", "orig", "rep")} | {"status": status, "failed": failed, "rc": code}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo"); ap.add_argument("pkg"); ap.add_argument("out")
    ap.add_argument("--tests", default="tests/agent")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--per-file", type=int, default=150)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--files", nargs="*", help="product files to mutate (default: all covered)")
    a = ap.parse_args()
    repo, out = Path(a.repo).resolve(), Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    cov = coverage_lines(repo, a.pkg, a.tests)
    tests = collect(repo, a.tests)
    (out / "tests.json").write_text(json.dumps(tests))
    rng = random.Random(a.seed)
    jobs = []
    for rel in sorted(cov):
        if a.files and rel not in a.files:
            continue
        p = repo / rel
        if not p.exists() or not cov[rel]:
            continue
        src = p.read_text()
        cands = candidates(p, cov[rel])
        rng.shuffle(cands)
        for m in cands[: a.per_file]:
            new = apply(src, m)
            if new is not None:
                jobs.append({**m, "file": rel, "src": new, "id": f"{rel}:{m['line']}:{m['col']}:{m['op']}"})
    (out / "mutants.json").write_text(json.dumps([{k: v for k, v in j.items() if k != "src"} for j in jobs]))
    print(f"{len(jobs)} mutants over {len(cov)} covered files, {len(tests)} tests", flush=True)
    with ProcessPoolExecutor(a.workers, initializer=init_worker, initargs=(repo, a.tests)) as ex, \
            (out / "kills.jsonl").open("w") as fh:
        for i, r in enumerate(ex.map(run_mutant, jobs, chunksize=1)):
            fh.write(json.dumps(r) + "\n")
            if i % 50 == 0:
                print(i, r["status"], flush=True)


if __name__ == "__main__":
    main()
