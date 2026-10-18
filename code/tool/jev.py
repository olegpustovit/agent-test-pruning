# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Jev (TypeSafe System One) client + CLI for typed questions over corpus texts.

  uv run tools/jev.py ping
  uv run tools/jev.py run  --venue V --questions analysis/questions.smoke.yaml --limit 5 --dry-run
  uv run tools/jev.py run  --venue V --questions analysis/questions.smoke.yaml --max-requests 50

Facts used (all from https://docs.typesafe.ai, read 2026-10-09; see analysis/JEV-NOTES-2026-10-09.md):
  POST https://api.typesafe.ai/v1/systemone, header `Authorization: Bearer <key>`,
  body {state, model, questions:{id:{type,instructions,criteria}}}; one state, many questions per request.
  Price $0.042 per million input tokens, output tokens free. Context 64k per request, 32k for state + longest question.

Security: the key is read from $JEV_API_KEY or parsed from ./.envrc inside this process only. It is never printed,
logged or written; every string that leaves this module (errors, ledger, answers) goes through scrub().
Only published papers/articles and synthetic text may be sent. This tool does not decide that; the caller does.
"""
from __future__ import annotations

import argparse, concurrent.futures as cf, hashlib, json, math, os, random, re, sys, threading, time
import urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
CACHE = ANALYSIS / "_cache"
LEDGER = CACHE / "requests.jsonl"
BASE_URL = "https://api.typesafe.ai"
PRICE_PER_MTOK = 0.042          # USD per million input tokens (docs /models); output tokens free
CHARS_PER_TOKEN = 3.8           # estimate; observed 3.87 chars/token on paper text (see notes)
REQUEST_OVERHEAD_TOKENS = 275   # observed: 275 input tokens for a 1-char state + 1 short question
STATE_TOKEN_LIMIT = 32000       # docs: state + longest question
REQUEST_TOKEN_LIMIT = 64000     # docs: state + all questions


# ---------------------------------------------------------------- key handling
_KEY: str | None = None


def api_key() -> str:
    global _KEY
    if _KEY is None:
        k = os.environ.get("JEV_API_KEY", "")
        if not k:
            envrc = ROOT / ".envrc"
            if envrc.exists():
                m = re.search(r"JEV_API_KEY\s*=\s*['\"]?([^'\"\s]+)", envrc.read_text())
                k = m.group(1) if m else ""
        if not k:
            raise SystemExit("JEV_API_KEY not found in environment or .envrc")
        _KEY = k
    return _KEY


def scrub(s) -> str:
    s = str(s)
    if _KEY:
        s = s.replace(_KEY, "***")
    s = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._\-]{8,}", r"\1***", s)
    s = re.sub(r"\b(sk|ts|tsk|key)[-_][A-Za-z0-9]{10,}\b", "***", s)
    return s


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


# ---------------------------------------------------------------- questions
def load_questions(path: Path) -> list[dict]:
    data = yaml.safe_load(Path(path).read_text())
    qs = data["questions"] if isinstance(data, dict) else data
    out, seen = [], set()
    for q in qs:
        for f in ("id", "kind", "text"):
            if f not in q:
                raise ValueError(f"question missing {f}: {q}")
        if q["id"] in seen:
            raise ValueError(f"duplicate question id {q['id']}")
        seen.add(q["id"])
        if q["kind"] not in ("choice", "score", "noul"):
            raise ValueError(f"bad kind {q['kind']}")
        if q["kind"] == "choice" and not q.get("options"):
            raise ValueError(f"{q['id']}: choice needs options")
        if q["kind"] == "score" and len(q.get("rubric") or []) < 2:
            raise ValueError(f"{q['id']}: score needs a rubric of >=2 levels")
        q.setdefault("applies_to", ["any"])
        q.setdefault("needs", "full")
        out.append(q)
    return out


def api_question(q: dict, shuffle_seed: int | None = None) -> dict:
    """Map a questions.yaml entry to the API question object."""
    if q["kind"] == "noul":
        d = {"type": "noul", "instructions": q["text"]}
        if q.get("criteria"):
            d["criteria"] = {"true": q["criteria"].get("true"), "false": q["criteria"].get("false")}
        return d
    if q["kind"] == "choice":
        opts = q["options"]
        items = list(opts.items()) if isinstance(opts, dict) else [(o, None) for o in opts]
        if shuffle_seed is not None:
            random.Random(f"{shuffle_seed}:{q['id']}").shuffle(items)
        return {"type": "choice", "instructions": q["text"], "criteria": dict(items)}
    return {"type": "score", "instructions": q["text"], "criteria": list(q["rubric"])}


# ---------------------------------------------------------------- documents / states
HEAD_NAMES = (r"abstract|introduction|related work|background|preliminaries|method(?:s|ology)?|approach|"
              r"evaluation|experiments?|results?|discussion|conclusions?|limitations?|threats to validity|"
              r"future work|references|acknowledg(?:e)?ments?|appendix")
HEAD_RES = [
    re.compile(r"^#{1,6}\s+\**(.+?)\**\s*$"),                                          # markdown (articles)
    re.compile(r"^(?:\d+(?:\.\d+){0,2}\.?|[A-Z]\.|[IVX]+\.)\s+[A-Z][^.!?]{2,90}$"),       # numbered / lettered
    re.compile(rf"^(?:{HEAD_NAMES})\.?$", re.I),                                      # bare standard names
]


def is_heading(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > 100 or "arXiv" in s:
        return False
    return any(r.match(s) for r in HEAD_RES)


def split_sections(text: str) -> list[tuple[str, str]]:
    """[(heading, body)] with a leading ('', preamble). Heuristic; PDF text is messy."""
    lines = text.splitlines()
    secs, cur_h, cur = [], "", []
    for i, ln in enumerate(lines):
        if is_heading(ln) and (i == 0 or not lines[i - 1].strip() or ln.strip().startswith("#")):
            secs.append((cur_h, "\n".join(cur).strip()))
            cur_h, cur = re.sub(r"^#+\s*", "", ln).strip(" *"), []
        else:
            cur.append(ln)
    secs.append((cur_h, "\n".join(cur).strip()))
    return secs


def est_tokens(s) -> int:
    if not isinstance(s, str):
        s = json.dumps(s, ensure_ascii=False)
    return math.ceil(len(s) / CHARS_PER_TOKEN)


class Doc:
    def __init__(self, item_id: str, text: str, title: str = "", venue: str = "", meta: dict | None = None):
        self.id, self.text, self.venue, self.meta = item_id, text, venue, meta or {}
        self.title = title or " ".join([l.strip() for l in text.splitlines() if l.strip()][:2])[:200]
        self.sections = split_sections(text)

    @property
    def abstract(self) -> str:
        m = re.search(r"(?im)^\s*abstract[.:—\- ]*\s*$|^\s*abstract[.:—\-]\s+", self.text)
        if m:
            seg = self.text[m.end():m.end() + 3000]
            cut = re.search(r"\n\s*(?:\d+\.?|I\.?)?\s*Introduction\b", seg)
            return (seg[:cut.start()] if cut else seg[:2200]).strip()
        return self.text[:1800].strip()

    def headings(self) -> list[str]:
        return [h for h, _ in self.sections if h]

    def section_text(self, pattern: str) -> tuple[str, list[str]]:
        rx = re.compile(pattern, re.I)
        hit = [(h, b) for h, b in self.sections if h and rx.search(h)]
        return "\n\n".join(f"## {h}\n{b}" for h, b in hit), [h for h, _ in hit]

    # --- strategies. every state is JSON-able; strategy name recorded with the answer
    @property
    def front_matter(self) -> str:
        """Author/affiliation block printed before the abstract (empty for articles without an Abstract marker)."""
        m = re.search(r"(?im)^\s*abstract[.:—\- ]*\s*$|^\s*abstract[.:—\-]\s+", self.text)
        return self.text[:m.start()][:2500].strip() if m else ""

    def state_abstract(self):
        st = {"title": self.title, "abstract": self.abstract}
        if self.front_matter:
            st["front_matter_with_authors_and_affiliations"] = self.front_matter
        return "abstract", st

    def state_whole(self):
        return "whole", {"title": self.title, "text": self.text}

    def state_digest(self, budget_tokens: int = 12000):
        heads = self.headings()
        skip = re.compile(r"references|acknowledg|appendix|bibliograph", re.I)
        body = [(h, b) for h, b in self.sections if h and not skip.search(h)]
        fixed = est_tokens({"title": self.title, "abstract": self.abstract, "section_headings": heads})
        per = max(300, int((budget_tokens - fixed) * CHARS_PER_TOKEN / max(1, len(body))))
        extracts = []
        for h, b in body:
            keep = b[:per]
            if re.search(r"limitation|threat|validity", h, re.I):
                keep = b[:3000]
            extracts.append({"heading": h, "extract": keep, "truncated": len(b) > len(keep)})
        return "digest", {"title": self.title, "abstract": self.abstract, "section_headings": heads,
                          "section_extracts": extracts}

    def state_section(self, pattern: str, budget_tokens: int = 12000):
        txt, names = self.section_text(pattern)
        txt = txt[: int(budget_tokens * CHARS_PER_TOKEN)]
        return ("section:" + "|".join(names)) if names else "section:none-found", {
            "title": self.title, "section": txt or "(no matching section found)",
            "section_headings": self.headings()}

    def build(self, need: str, section: str | None, force: str | None, budget: int):
        if force == "abstract" or (need == "abstract" and not force):
            return self.state_abstract()
        if section and not force:
            s = self.state_section(section, min(budget, 12000))
            if not s[0].endswith("none-found"):
                return s
        if force == "digest":
            return self.state_digest()
        name, st = self.state_whole()
        if force == "whole" or est_tokens(st) <= budget:
            return name, st
        return self.state_digest()


def load_docs(a) -> list[Doc]:
    vdir = ROOT / "corpus" / a.venue if a.venue else None
    tdir = Path(a.text_dir) if a.text_dir else (vdir / "text" if vdir else None)
    meta = {}
    items = Path(a.items_file) if a.items_file else (vdir / "items.jsonl" if vdir else None)
    if items and items.exists():
        for ln in items.read_text().splitlines():
            if ln.strip():
                r = json.loads(ln)
                meta[r["id"]] = r
    docs = []
    for p in sorted(tdir.glob("*.txt")):
        if a.ids and p.stem not in a.ids:
            continue
        m = meta.get(p.stem, {})
        docs.append(Doc(p.stem, p.read_text(errors="replace"), m.get("title", ""), a.venue or "", m))
    return docs[: a.limit] if a.limit else docs


# ---------------------------------------------------------------- backends
class Backend:
    name = "base"

    def ask(self, state, questions: dict, model: str) -> dict:
        """Return {'answers':{id:{...api-shaped...}}, 'usage':{...}, 'model':str, 'request_id':str|None}."""
        raise NotImplementedError


class HttpError(Exception):
    def __init__(self, status, body, headers=None):
        super().__init__(f"HTTP {status}: {scrub(body)[:400]}")
        self.status, self.body, self.headers = status, scrub(body), headers or {}


class TypeSafeBackend(Backend):
    name = "typesafe"

    def __init__(self, timeout: float = 120.0):
        self.timeout = timeout

    def ask(self, state, questions, model):
        body = json.dumps({"state": state, "model": model, "questions": questions}, ensure_ascii=False).encode()
        req = urllib.request.Request(BASE_URL + "/v1/systemone", data=body, method="POST", headers={
            "Authorization": "Bearer " + api_key(), "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as f:
                rid = f.headers.get("x-typesafe-request-id")
                out = json.loads(f.read().decode())
                out["request_id"] = rid
                return out
        except urllib.error.HTTPError as e:
            raise HttpError(e.code, e.read().decode(errors="replace"), dict(e.headers))


class AdapterBackend(Backend):
    """Interface only: runs the same questions through github.com/typesafe-ai/system-one-adapter-python
    (MIT) so another LLM can be compared. Not wired to any paid third-party key; needs
    `uv run --with system-one-adapter[openai|anthropic|gemini]` and that provider's own env key at call time.
    UNTESTED."""
    name = "adapter"

    def __init__(self, provider: str = "openai", **kw):
        self.provider, self.kw = provider, kw

    def ask(self, state, questions, model):
        from system_one_adapter import SystemOneAdapterClient  # type: ignore
        client = SystemOneAdapterClient(structured_outputs=True, llm_answer_mode="probabilities",
                                        normalize_probabilities=True)
        t = time.time()
        r = client.system_one(state=state, questions=questions, provider=self.provider, model=model)
        d = r.model_dump()
        d.setdefault("model", f"{self.provider}:{model}")
        d["request_id"] = None
        d["adapter_latency_s"] = time.time() - t
        return d


def make_backend(name: str) -> Backend:
    if name == "typesafe":
        return TypeSafeBackend()
    if name.startswith("adapter"):
        return AdapterBackend(*(name.split(":", 1)[1:2] or ["openai"]))
    raise SystemExit(f"unknown backend {name}")


# ---------------------------------------------------------------- engine
class Limiter:
    def __init__(self, rps: float):
        self.gap, self.lock, self.next = (1.0 / rps if rps > 0 else 0), threading.Lock(), 0.0

    def wait(self):
        with self.lock:
            t = max(time.monotonic(), self.next)
            self.next = t + self.gap
        d = t - time.monotonic()
        if d > 0:
            time.sleep(d)


class Caps:
    """Hard caps. Per-invocation (--max-requests/--max-input-tokens) and lifetime budget from the ledger."""

    def __init__(self, max_requests, max_tokens, budget_requests, budget_usd):
        self.lock = threading.Lock()
        self.max_requests, self.max_tokens = max_requests, max_tokens
        self.req = self.tok = 0
        prev_req, prev_tok = ledger_totals()
        self.budget_requests = budget_requests - prev_req
        self.budget_tokens = int(budget_usd / PRICE_PER_MTOK * 1e6) - prev_tok
        self.stopped = None

    def reserve(self, est_tokens_: int) -> bool:
        with self.lock:
            why = None
            if self.req + 1 > self.max_requests:
                why = "--max-requests"
            elif self.tok + est_tokens_ > self.max_tokens:
                why = "--max-input-tokens"
            elif self.req + 1 > self.budget_requests:
                why = "lifetime request budget"
            elif self.tok + est_tokens_ > self.budget_tokens:
                why = "lifetime USD budget"
            if why:
                self.stopped = self.stopped or why
                return False
            self.req += 1
            self.tok += est_tokens_
            return True


def ledger_totals() -> tuple[int, int]:
    n = t = 0
    if LEDGER.exists():
        for ln in LEDGER.read_text().splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            n += 1
            t += r.get("input_tokens") or r.get("est_input_tokens") or 0
    return n, t


_ledger_lock = threading.Lock()


def ledger_add(rec: dict):
    CACHE.mkdir(parents=True, exist_ok=True)
    with _ledger_lock, LEDGER.open("a") as f:
        f.write(scrub(json.dumps(rec, ensure_ascii=False)) + "\n")


def send(backend: Backend, state, qs: dict, model: str, limiter: Limiter, caps: Caps, est_in: int,
         attempts: int = 6, tag: str = ""):
    """One request with retries. Returns (response_dict, latency_s) or raises. Every attempt is counted + ledgered."""
    err = None
    for i in range(attempts):
        if not caps.reserve(est_in):
            raise RuntimeError(f"cap reached: {caps.stopped}")
        limiter.wait()
        t0 = time.time()
        rec = {"at": now(), "tag": tag, "backend": backend.name, "model": model, "n_questions": len(qs),
               "est_input_tokens": est_in, "attempt": i}
        try:
            r = backend.ask(state, qs, model)
            lat = time.time() - t0
            rec.update(status=200, latency_s=round(lat, 3), input_tokens=(r.get("usage") or {}).get("input_tokens"),
                       output_tokens=(r.get("usage") or {}).get("output_tokens"), request_id=r.get("request_id"))
            ledger_add(rec)
            return r, lat
        except HttpError as e:
            rec.update(status=e.status, latency_s=round(time.time() - t0, 3), error=e.body[:300])
            ledger_add(rec)
            err = e
            if e.status not in (429, 500, 502, 503, 504, 529):
                raise
            ra = e.headers.get("retry-after") or e.headers.get("Retry-After")
            delay = float(ra) if ra and re.fullmatch(r"[\d.]+", ra) else min(60, 2 ** i)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            rec.update(status=None, latency_s=round(time.time() - t0, 3), error=scrub(e)[:300])
            ledger_add(rec)
            err = e
            delay = min(60, 2 ** i)
        time.sleep(delay * (0.75 + random.random() / 2))
    raise RuntimeError(scrub(f"gave up after {attempts} attempts: {err}"))


def cache_key(model: str, state, qobj: dict) -> str:
    blob = json.dumps({"m": model, "s": state, "q": qobj}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()


def cache_get(key):
    p = CACHE / key[:2] / f"{key}.json"
    return json.loads(p.read_text()) if p.exists() else None


def cache_put(key, rec):
    p = CACHE / key[:2] / f"{key}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(scrub(json.dumps(rec, ensure_ascii=False)))


def normalise(q: dict, ans: dict) -> dict:
    t = ans.get("type")
    if t == "noul":
        p = ans.get("noul")
        return {"answer": p, "probabilities": None, "confidence": abs(2 * p - 1) if p is not None else None,
                "confidence_derived": True}
    if t == "choice":
        return {"answer": ans.get("choice"), "probabilities": ans.get("probabilities"),
                "confidence": ans.get("confidence"), "confidence_derived": False}
    if t == "score":
        return {"answer": ans.get("score"), "probabilities": ans.get("probabilities"),
                "confidence": ans.get("confidence"), "confidence_derived": False}
    return {"answer": None, "probabilities": None, "confidence": None, "confidence_derived": False, "error": "unknown answer type"}


def plan_requests(docs, questions, a):
    """[(doc, strategy, state, [questions])] — one request per distinct state, <= max_q questions each."""
    plan = []
    for d in docs:
        groups: dict[str, tuple[str, object, list]] = {}
        for q in questions:
            if a.doc_type != "any" and "any" not in q["applies_to"] and a.doc_type not in q["applies_to"]:
                continue
            strat, st = d.build(q["needs"], q.get("section"), a.force_strategy, a.state_budget)
            k = json.dumps(st, sort_keys=True, ensure_ascii=False)
            groups.setdefault(k, (strat, st, []))[2].append(q)
        for strat, st, qs in groups.values():
            for i in range(0, len(qs), a.max_q):
                plan.append((d, strat, st, qs[i:i + a.max_q]))
    return plan


def run(a) -> int:
    questions = load_questions(a.questions)
    if a.only:
        questions = [q for q in questions if q["id"] in a.only]
    docs = load_docs(a)
    plan = plan_requests(docs, questions, a)
    backend = make_backend(a.backend)
    model = a.model

    jobs, cached_rows = [], []
    for d, strat, st, qs in plan:
        todo, st_tok = [], est_tokens(st)
        for q in qs:
            qo = api_question(q, a.shuffle_seed)
            key = cache_key(model, st, qo)
            hit = None if a.no_cache else cache_get(key)
            (cached_rows.append((d, strat, st_tok, q, key, hit)) if hit else todo.append((q, qo, key)))
        if todo:
            est = st_tok + sum(est_tokens(qo) for _, qo, _ in todo) + REQUEST_OVERHEAD_TOKENS
            jobs.append((d, strat, st, st_tok, todo, est))

    tot_est = sum(j[5] for j in jobs)
    print(f"plan: {len(docs)} docs, {len(questions)} questions -> {len(plan)} request groups; "
          f"{len(jobs)} to send, {sum(len(j[4]) for j in jobs)} questions uncached, "
          f"{len(cached_rows)} answers from cache", file=sys.stderr)
    from collections import Counter
    print("strategies:", dict(Counter(j[1].split(":")[0] for j in jobs)), file=sys.stderr)
    print(f"estimated input tokens: {tot_est:,} (chars/token={CHARS_PER_TOKEN}, overhead={REQUEST_OVERHEAD_TOKENS}/req); "
          f"estimated cost ${tot_est * PRICE_PER_MTOK / 1e6:.4f}; largest request ~{max([j[5] for j in jobs] or [0]):,} tokens",
          file=sys.stderr)
    over = [j for j in jobs if j[5] > STATE_TOKEN_LIMIT and not a.allow_over_limit]
    if over:
        print(f"WARNING: {len(over)} requests estimated above the documented {STATE_TOKEN_LIMIT} state limit "
              f"(use --allow-over-limit to send anyway)", file=sys.stderr)
    if a.dry_run:
        for d, strat, st, st_tok, todo, est in jobs[: a.show]:
            print(f"  {d.id} strategy={strat} state~{st_tok} tok est~{est} q={[q['id'] for q, _, _ in todo]}", file=sys.stderr)
        return 0
    jobs = [j for j in jobs if j[5] <= STATE_TOKEN_LIMIT or a.allow_over_limit]

    caps = Caps(a.max_requests, a.max_input_tokens, a.budget_requests, a.budget_usd)
    limiter = Limiter(a.rps)
    out_dir = ANALYSIS / (a.venue or a.out_name or "adhoc")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path(a.out) if a.out else out_dir / "answers.jsonl"
    have = set()
    if out_path.exists():
        for ln in out_path.read_text().splitlines():
            r = json.loads(ln)
            have.add((r["item_id"], r["question_id"], r.get("cache_key")))
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    wlock = threading.Lock()
    stats = {"sent": 0, "errors": 0, "rows": 0}

    def write(row):
        k = (row["item_id"], row["question_id"], row["cache_key"])
        with wlock:
            if k in have and not a.no_cache:
                return
            have.add(k)
            with out_path.open("a") as f:
                f.write(scrub(json.dumps(row, ensure_ascii=False)) + "\n")
            stats["rows"] += 1

    def base_row(d, strat, st_tok, q, key):
        return {"item_id": d.id, "venue": d.venue, "question_id": q["id"], "kind": q["kind"], "strategy": strat,
                "state_tokens_est": st_tok, "cache_key": key, "model_requested": model, "backend": backend.name,
                "run_id": run_id}

    for d, strat, st_tok, q, key, hit in cached_rows:
        r = base_row(d, strat, st_tok, q, key)
        r.update(hit, cached=True)
        write(r)

    def do(job):
        d, strat, st, st_tok, todo, est = job
        qmap = {q["id"]: qo for q, qo, _ in todo}
        try:
            resp, lat = send(backend, st, qmap, model, limiter, caps, est, tag=a.tag)
        except Exception as e:  # noqa: BLE001
            with wlock:
                stats["errors"] += 1
            for q, _, key in todo:
                r = base_row(d, strat, st_tok, q, key)
                r.update(answer=None, error=scrub(e)[:300], requested_at=now(), cached=False)
                write(r)
            return
        stats["sent"] += 1
        usage = resp.get("usage") or {}
        for q, _, key in todo:
            ans = resp.get("answers", {}).get(q["id"], {})
            r = base_row(d, strat, st_tok, q, key)
            r.update(normalise(q, ans))
            r.update(request_input_tokens=usage.get("input_tokens"), request_output_tokens=usage.get("output_tokens"),
                     request_questions=len(todo), latency_s=round(lat, 3), requested_at=now(),
                     model=resp.get("model"), request_id=resp.get("request_id"), cached=False)
            if ans:
                cache_put(key, {k: v for k, v in r.items() if k not in ("item_id", "venue", "run_id", "cache_key", "cached")})
            write(r)

    with cf.ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(do, jobs))
    print(f"done: sent={stats['sent']} errors={stats['errors']} rows_written={stats['rows']} "
          f"requests_this_run={caps.req} est_tokens={caps.tok:,} stopped={caps.stopped} -> {out_path}", file=sys.stderr)
    return 1 if stats["errors"] or caps.stopped else 0


# ---------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ping", help="list models (also checks auth)")
    r = sub.add_parser("run", help="plan and (unless --dry-run) send questions over documents")
    r.add_argument("--venue"); r.add_argument("--text-dir"); r.add_argument("--items-file")
    r.add_argument("--questions", type=Path, default=ANALYSIS / "questions.yaml")
    r.add_argument("--only", nargs="*", help="question ids"); r.add_argument("--ids", nargs="*")
    r.add_argument("--limit", type=int); r.add_argument("--doc-type", default="any")
    r.add_argument("--model", default="jev-latest"); r.add_argument("--backend", default="typesafe",
                   help="typesafe | adapter[:openai|anthropic|gemini] (adapter = interface only, untested)")
    r.add_argument("--force-strategy", choices=["abstract", "whole", "digest"])
    r.add_argument("--state-budget", type=int, default=28000, help="est. tokens a whole-paper state may use")
    r.add_argument("--max-q", type=int, default=40, help="questions per request")
    r.add_argument("--max-requests", type=int, required=True)
    r.add_argument("--max-input-tokens", type=int, default=2_000_000)
    r.add_argument("--budget-requests", type=int, default=2000, help="lifetime cap over analysis/_cache/requests.jsonl")
    r.add_argument("--budget-usd", type=float, default=2.0, help="lifetime cap (input tokens x price)")
    r.add_argument("--workers", type=int, default=4); r.add_argument("--rps", type=float, default=5.0)
    r.add_argument("--no-cache", action="store_true"); r.add_argument("--shuffle-seed", type=int)
    r.add_argument("--allow-over-limit", action="store_true"); r.add_argument("--dry-run", action="store_true")
    r.add_argument("--show", type=int, default=10); r.add_argument("--out"); r.add_argument("--out-name")
    r.add_argument("--tag", default="")
    c = sub.add_parser("corpus", help="routed, batched, resumable run over corpus/*/text (see tools/jevcorpus.py)")
    c.add_argument("--venue", nargs="*"); c.add_argument("--ids", nargs="*"); c.add_argument("--limit", type=int)
    c.add_argument("--only-ids-file", help="JSON list of [venue, id] pairs"); c.add_argument("--questions")
    c.add_argument("--only", nargs="*"); c.add_argument("--model", default="jev-1.13.0")
    c.add_argument("--max-q", type=int, default=50, help="questions per request (notes: 40-60)")
    c.add_argument("--max-requests", type=int, required=True); c.add_argument("--max-input-tokens", type=int, default=300_000_000)
    c.add_argument("--budget-requests", type=int, default=40000); c.add_argument("--budget-usd", type=float, default=15.0)
    c.add_argument("--workers", type=int, default=8); c.add_argument("--rps", type=float, default=10.0)
    c.add_argument("--reps", type=int, default=1, help="repeats per state/question (1 = main run; 3 = test-retest)")
    c.add_argument("--shuffle", action="store_true", help="add one random option order for Choice"); c.add_argument("--paraphrases")
    c.add_argument("--no-cache", action="store_true"); c.add_argument("--dry-run", action="store_true"); c.add_argument("--skip-roles", action="store_true")
    c.add_argument("--out-name", default="answers.jsonl"); c.add_argument("--tag", default="corpus")
    a = ap.parse_args()
    if a.cmd == "corpus":
        import jevcorpus
        return jevcorpus.run_corpus(a)
    if a.cmd == "ping":
        req = urllib.request.Request(BASE_URL + "/v1/models", headers={"Authorization": "Bearer " + api_key()})
        try:
            with urllib.request.urlopen(req, timeout=30) as f:
                print(scrub(f.read().decode()))
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code}: {scrub(e.read().decode(errors='replace'))[:300]}")
            return 1
        return 0
    if not (a.venue or a.text_dir):
        ap.error("--venue or --text-dir required")
    return run(a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print("error:", scrub(e), file=sys.stderr)
        sys.exit(2)
