# Subject selection rule (written 2026-10-18, before any measurement or agent run)

Candidates: well-known pure-Python open-source libraries on GitHub, listed below in the order they were thought of; no candidate is added after measuring.

Eligible when all hold, measured by `measure_subjects.py` at the head of the default branch:
1. OSI permissive licence (MIT, BSD, Apache-2.0).
2. Product code (package directory, `.py`, non-blank lines, tests excluded) between 4,000 and 30,000 lines.
3. Its own pytest suite passes and runs in under 120 seconds on kyiv-grid with one worker.
4. The window: the last 120 non-merge commits on the default branch that change product `.py` files; at least 15 of them have a message matching `\b(fix|bug|regression|issue #?\d+)\b` (case-insensitive) and change product code.
5. Pure Python: no compiled extension needed to run its tests.

Ordering: eligible candidates ranked by the number of bug-fix commits in the window (rule 4), ties by smaller test runtime. The top two are used; the third is a reserve if one fails during the harness smoke test (the reason is recorded).

Candidates: marshmallow, click, attrs, arrow, tomlkit, python-slugify, humanize, cattrs, jinja, itsdangerous, boltons, python-dateutil, tabulate, pendulum, schedule.

## Measurement (2026-10-18, kyiv-grid, harness/measure_subjects.py)
Pass 1 failed on most candidates because the script did not install declared test dependencies (a measurement fault); the installer was fixed (extras, PEP 735 groups, requirement files) and the failed candidates re-measured; tomlkit needed its declared git submodule (tests/toml-test) initialised. The rule was not changed.

| Candidate | Licence | Product lines | Window fixes | Suite | Eligible |
|---|---|---|---|---|---|
| tomlkit | MIT | 5,162 | 48 | 1203 passed, 1.0 s | yes |
| boltons | BSD | 14,566 | 45 | 525 passed, 2.3 s | yes |
| marshmallow | MIT | 4,156 | 34 | 1190 passed, 1.5 s | yes |
| click | BSD | 9,832 | 33 | 2262 passed, 3.8 s | yes |
| arrow | Apache | 8,904 | 25 | 1902 passed, 8.2 s | yes |
| jinja | BSD | 11,431 | 24 | 911 passed, 1.8 s | yes |
| attrs | MIT | 5,181 | 19 | 1 failed at head | no (rule 3) |
| cattrs | MIT | 5,852 | 25 | collection error | no (rule 3) |
| humanize | none found | 1,375 | 35 | passes | no (rules 1, 2) |
| tabulate, schedule, python-slugify, itsdangerous | permissive | < 4,000 | | | no (rule 2) |
| python-dateutil | Apache | 6,233 | 0 (4 commits touch src/dateutil) | error | no (rules 3, 4) |
| pendulum | MIT | 12,333 | 20 of 55 | compiled extension, no pytest | no (rules 3-5) |

Selected: tomlkit and boltons. Reserve: marshmallow.
