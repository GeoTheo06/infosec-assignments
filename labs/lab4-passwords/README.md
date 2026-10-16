# Lab 4 — Password-database breach benchmark

Offline, synthetic exercise comparing four storage schemes (unsalted SHA-256,
shared-salt, per-row salt, expensive PBKDF2) and measuring work reuse across
accounts and releases. Bonus: lookup table vs genuine rainbow table.

## Layout

```
lab4-passwords/
├─ passlab/                library (NOT student-editable)
│  ├─ schemes.py           A/B/C/D constructions + counted HashOracle
│  ├─ candidates.py        fixed-order 512 candidates (+ absent passwords)
│  ├─ generator.py         seeded fixtures (A–C share assignment) + manifest
│  ├─ runner.py            instrumented runner; recovery vs full-pass; grouping
│  ├─ reuse.py             cross-release / cross-salt reuse experiment
│  ├─ benchmark.py         monotonic timing harness + iteration calibration
│  └─ hashcat_export.py    export to Hashcat modes 1400 / 1410 / 10900
├─ student/
│  ├─ strategy.py          ← students implement recover(...)
│  ├─ bonus_stub.py        ← bonus: build_rainbow_table + rainbow_lookup
│  └─ HANDOUT.md
├─ ta/reference_strategy.py   ← TA reference recovery strategy (do not ship)
├─ bonus/
│  ├─ rainbow.py           scaffolding: domain, hash, reduce, walk, counters
│  ├─ reference.py         TA reference rainbow build + lookup (do not ship)
│  └─ grade.py             bonus grader
├─ grader/grade.py         main grader (fresh fixtures, recomputed counts)
├─ tests/test_passwords.py pytest (14 tests)
├─ conftest.py
└─ README.md
```

## Run / grade / test

```bash
pip install -r ../../workspace/requirements.txt    # stdlib-only lab; pytest to test

python -m grader.grade --strategy ta.reference_strategy --rounds 2   # PASS
python -m grader.grade --strategy student.strategy                   # FAIL until done
python -m bonus.grade  --module  bonus.reference                     # PASS
pytest tests -q                                                      # 14 tests
```

Verified headline counts (512 candidates, 12 accounts, distinct salts):
**A = 512, B = 512, C = 6144** full-pass evaluations; scheme D small fixture
(2 accounts × 128 candidates) = 256. Recovery mode does ≤ that (early stop),
except where out-of-list/absent passwords force a full scan.

## Design notes mapped to the brief

| Brief point | Implementation |
|---|---|
| Exact schemes A/B/C/D with unambiguous encoding; salt chars hashed, not decoded | `passlab/schemes.py` (`_salt_bytes` encodes the hex string's ASCII). |
| 12 accounts, 512 fixed candidates, repeats, some out-of-list; shared A–C selection | `generator.make_assignment` + `build_fixture`; `candidates.py`. |
| Second release for reuse; regenerate salts without changing difficulty | `make_release(..., release=2)`; salts seeded by (seed,scheme,release). |
| Scheme D small paired benchmark, several iteration counts, calibrate ~minutes | `make_d_release`, `benchmark.compare_iterations`, `benchmark.calibrate_iterations`. |
| Instrumented runner; recovery + controlled full-pass; authoritative counters | `runner.run`; counts come from `HashOracle`, not the student. |
| Grouped counts: A=512, B=512, C=6144; naive does more | grouping in `runner.group_by_salt`; reference groups by salt. |
| Reuse: no salt / same shared / changed shared / new individual | `reuse.run_reuse_experiment`. |
| Hashcat export 1400/1410/10900, tested | `hashcat_export.py`; `tests` check mode + shape. |
| Grader validates accounts + reruns strategy on unseen fixtures; recomputes work | `grader/grade.py` (fresh seeds, trusted oracle). |
| Bonus: 1024-word domain, position-dependent reduction, chains, verify; partial coverage | `bonus/`. |

## Reset procedure

Fixtures are generated deterministically from a seed; there is no persisted
state. To "reset" or re-issue, pick a new seed (the grader already uses fresh,
unseen seeds per run). Regenerate salts via the `release=` parameter without
changing difficulty. Pilot scheme D independently (`benchmark.calibrate_iterations`)
so its runtime cannot stall the rest of the assignment.

## Shipping to students

Ship `passlab/`, `student/`, `bonus/rainbow.py`, `conftest.py`. **Do not ship**
`ta/` or `bonus/reference.py`. The graders may ship (they import the student
module) but the real grade runs server-side on fresh fixtures.
