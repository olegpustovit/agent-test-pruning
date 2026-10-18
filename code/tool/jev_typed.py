# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Jev (TypeSafe System One) answers the method's four facet questions about every test.

The facets (oracle, subject, real_code, risk_area), their option weights and the answering rules are in
jev_facets.json. Each request carries one test as the state: its source, the helpers of its file, the product
functions it executes, and parser facts counted from the code. A fifth question asks Jev for a 1-5 usefulness
score, used only as the "Jev usefulness" baseline. Output: one JSON line per test, read by testprune.py quality.

uv run jev_typed.py <reach.json> <repo> <out.jsonl> [--budget-requests N] [--workers 8]
"""
import argparse, json, re, sys, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # jev.py sits next to this file
import jev  # noqa: E402

FACETS = json.loads((Path(__file__).parent / "jev_facets.json").read_text())
RULES = " ".join(FACETS["rules"])
QUESTIONS = {f["name"]: {"type": "choice", "instructions": f"{f['goal']} {RULES}", "criteria": f["options"]}
             for f in FACETS["facets"]}
QUESTIONS["usefulness"] = {"type": "score", "instructions": f"How much would the test suite lose if this one test were deleted? {RULES}",
                           "criteria": ["Nothing: it could not fail on a realistic bug.", "Little: it runs code but checks almost nothing.",
                                        "Some: it checks real behaviour weakly or repeats nearby tests.",
                                        "Much: it checks meaningful behaviour with concrete assertions.",
                                        "A lot: it checks behaviour users rely on and would catch a bug other tests miss."]}
ASSERT = re.compile(r"\bassert\w*\b|\.(Error|Errorf|Fatal|Fatalf|Fail|FailNow)\(|\brequire\.|\bexpect\(|\.toBe|\.toEqual")
MOCK = re.compile(r"mock|Mock|fake|Fake|stub|Stub|patch|monkeypatch|spy|Spy")


def test_file(repo: Path, tid: str):
    """The file a test lives in: Python ids are path::name, Go ids are package-dir::TestName."""
    left, _, name = tid.partition("::")
    if left.endswith(".py") or left.endswith(".ts"):
        return repo / left, name.split("::")[-1].split("[")[0]
    for f in sorted((repo / left).glob("*_test.go")):
        if re.search(rf"^func {re.escape(name)}\(", f.read_text(errors="ignore"), re.M):
            return f, name
    return None, name


def state_for(R, repo, t):
    src = R["sources"].get(t, "")
    f, name = test_file(repo, t)
    helpers = ""
    if f and f.exists():
        whole = f.read_text(errors="ignore")
        helpers = whole.replace(src, "") if src else whole
    facts = {"test_lines": len(src.splitlines()), "assertions": len(ASSERT.findall(src)), "mock_mentions": len(MOCK.findall(src)),
             "product_functions_executed": len(R["tests"][t]["symbols"])}
    reach = ", ".join(R["tests"][t]["symbols"][:20]) or "none"
    return (f"Test: {t}\nparser_facts: {json.dumps(facts)}\nProduct functions it executes: {reach}\n\n"
            f"Test source:\n{src[:10000]}\n\nhelpers_and_fixtures_from_same_file:\n{helpers[:6000]}"), facts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reach"); ap.add_argument("repo"); ap.add_argument("out")
    ap.add_argument("--budget-requests", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--model", default="jev-1.13.0")
    a = ap.parse_args()
    R = json.loads(Path(a.reach).read_text())
    repo, out = Path(a.repo).resolve(), Path(a.out)
    done = {json.loads(l)["test"] for l in out.read_text().splitlines()} if out.exists() else set()
    todo = [t for t in sorted(R["tests"]) if t not in done]
    backend, limiter = jev.make_backend("typesafe"), jev.Limiter(4.0)
    prev, _ = jev.ledger_totals()
    caps = jev.Caps(len(todo) * 3 + 10, 80_000_000, a.budget_requests or prev + len(todo) * 3 + 10, 15.0)
    lock = threading.Lock()

    def one(t):
        state, facts = state_for(R, repo, t)
        key = jev.cache_key(a.model, state, QUESTIONS)
        r = jev.cache_get(key)
        if r is None:
            r, _ = jev.send(backend, state, QUESTIONS, a.model, limiter, caps, jev.est_tokens(state) + 1500, tag="testprune-facets")
            jev.cache_put(key, r)
        ans = r.get("answers", {})
        row = {"test": t, "model": a.model, "parser_facts": facts}
        for q, spec in QUESTIONS.items():
            kind = "choice" if spec["type"] == "choice" else "score"
            n = jev.normalise({"kind": kind}, ans.get(q, {}))
            row[q] = n["answer"]
            row[q + "_p"] = n["probabilities"]
        if isinstance(row.get("usefulness"), (int, float)):
            row["grade"] = int(row["usefulness"]) + 1  # score levels are 0-based; 1-5 like the rubric
        with lock, out.open("a") as fh:
            fh.write(json.dumps(row) + "\n")

    def safe(t):
        try:
            one(t)
        except Exception as exc:
            print(f"{t}: {jev.scrub(exc)[:200]}", file=sys.stderr)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(safe, todo))
    print(f"{len(todo)} tests asked; ledger requests now {jev.ledger_totals()[0]}")


if __name__ == "__main__":
    main()
