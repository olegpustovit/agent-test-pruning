# Which tests to keep when a coding agent writes the test suite: scripts and data

Artifacts for the paper "Which Tests to Keep When a Coding Agent Writes the Test Suite" (SANER 2027 Industrial Track submission). Everything here comes from public projects and from the author's own open-source tool agentpack.

## What is here
- `code/harness/`
  - `replay.py`: replays the last 120 commits that change product code of a Python library. At each commit, Claude Code is asked to add tests for the change under `tests/agent`; the product code equals upstream at every step.
  - `mutate.py`, `faults.py`: planted bugs (eight mutation operators) and real bugs (reverted bug-fix commits), with per-test kill sets.
  - `stats.py`, `cluster_stats.py`: shares kept at a budget, bootstrap intervals, sign tests by mutant and by file.
  - `measure_subjects.py`, `measure_own.py`, `analyze.py`.
- `code/tool/`
  - `testprune.py`: the signals as orders (coverage, risk reach, judge, combined order, CI order, CI floor via `blend`/orders), grading, evaluation.
  - `jev_typed.py` + `jev.py` + `jev_facets.json`: the four facet questions asked of Jev (TypeSafe System One, jev-1.13.0) per test. Needs `JEV_API_KEY`.
  - `ci_mine.py`: catch labels from GitHub Actions history.
  - `go_adapter.py` + `gohelper/`: the same inputs for a Go module.
  - `ts_adapter.py` + `tshelper/`: static import reach for a TypeScript/Bun project.
  - `rubric.md`: the grading rubric.
- `SUBJECTS.md`: the subject selection rule, written before any measurement, and its outcome.
- `data/<subject>/`: reach (per-test coverage), mutants and kill sets (`mut/`), real bugs (`flt/`), grades (`grades-*.jsonl`, `jev-facets.jsonl`), orders (`order-*.json`, `keep-ask2.json`), results (`stats.json`, `cluster10.json`); agentpack also has `ci-labels.jsonl` and `tiers.json`.
- `data/replays/<run>/`: each replay's configuration, per-step log (`state.jsonl`, including agent cost) and the agent-written tests (`tests-agent/`).

## Running
Python scripts carry inline metadata; run them with `uv run <script>.py --help`. Replays need Claude Code logged in; grading needs Claude Code; Jev needs a TypeSafe key.
