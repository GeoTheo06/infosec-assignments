#!/usr/bin/env python3
"""Grader for Lab 4 (password benchmark).

Reruns a submitted recovery strategy on FRESH, unseen fixtures and recomputes
all work counts in the trusted harness (the oracle), never trusting
self-reported numbers. Checks:

  * in-list passwords are recovered; out-of-list passwords are not;
  * no wrong mappings;
  * controlled full-pass evaluation counts equal distinct_salts * candidates
    (A=512, B=512, C=6144 for 512 candidates), independent of early stopping;
  * recovery mode never does MORE work than full-pass.

Usage (from labs/lab4-passwords):
    python -m grader.grade --strategy ta.reference_strategy
    python -m grader.grade --strategy student.strategy --rounds 3
    python -m grader.grade --strategy path/to/strategy.py
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_ROOT))

from passlab.generator import make_d_release, make_release   # noqa: E402
from passlab.runner import run                                # noqa: E402

GRADER_SEED_BASE = 90_000
D_ITERATIONS = 1_000   # small so the grader stays fast; release calibrates higher


def _load_strategy(spec: str):
    if spec.endswith(".py"):
        path = Path(spec).resolve()
        ms = importlib.util.spec_from_file_location("submitted_strategy", path)
        mod = importlib.util.module_from_spec(ms)
        ms.loader.exec_module(mod)  # type: ignore[union-attr]
    else:
        mod = importlib.import_module(spec)
    return getattr(mod, "recover")


def _check_fixture(fixture, strategy, candidates_len) -> dict:
    full = run(fixture, strategy, full_pass=True)
    rec = run(fixture, strategy, full_pass=False)
    expected_full = full["distinct_salts"] * full["candidates"]
    checks = {
        "all_in_list_recovered": full["recovered_correct"] == full["recoverable_in_list"],
        "no_wrong": full["recovered_wrong"] == 0,
        "fullpass_count_exact": full["evaluations"] == expected_full,
        "recovery_not_more_than_fullpass": rec["evaluations"] <= full["evaluations"],
        "recovery_correct": rec["recovered_correct"] == rec["recoverable_in_list"],
    }
    return {
        "scheme": fixture.scheme,
        "expected_fullpass_evaluations": expected_full,
        "fullpass_evaluations": full["evaluations"],
        "recovery_evaluations": rec["evaluations"],
        "recovered_correct": full["recovered_correct"],
        "recoverable_in_list": full["recoverable_in_list"],
        "recovered_wrong": full["recovered_wrong"],
        "checks": checks,
        "ok": all(checks.values()),
    }


def grade(strategy, rounds: int = 3) -> dict:
    results = []
    all_ok = True
    for i in range(rounds):
        seed = GRADER_SEED_BASE + i
        per_round = {}
        for scheme in ("A", "B", "C"):
            fx = make_release(seed, scheme)
            per_round[scheme] = _check_fixture(fx, strategy, 512)
        # scheme D small/fast fixture
        d_fx = make_d_release(seed, D_ITERATIONS)
        per_round["D"] = _check_fixture(d_fx, strategy, 128)
        round_ok = all(r["ok"] for r in per_round.values())
        all_ok = all_ok and round_ok
        results.append({"seed": seed, "ok": round_ok, "schemes": per_round})
    return {"passed": all_ok, "rounds": rounds, "results": results}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lab 4 password-benchmark grader")
    ap.add_argument("--strategy", required=True,
                    help="dotted module (ta.reference_strategy) or path to .py")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        strategy = _load_strategy(args.strategy)
        report = grade(strategy, rounds=args.rounds)
    except NotImplementedError as exc:
        report = {"passed": False, "error": f"not implemented: {exc}", "results": []}
    except Exception as exc:
        report = {"passed": False, "error": f"{type(exc).__name__}: {exc}", "results": []}

    if args.json:
        import json
        print(json.dumps(report, indent=2))
        return 0 if report.get("passed") else 1

    verdict = "PASS" if report.get("passed") else "FAIL"
    print(f"Lab 4 password grader ({args.strategy}) — {verdict}")
    if report.get("error"):
        print(f"  {report['error']}")
        return 1
    for rnd in report["results"]:
        tag = "OK " if rnd["ok"] else "XX "
        print(f"  [{tag}] seed {rnd['seed']}")
        for scheme, r in rnd["schemes"].items():
            m = "ok " if r["ok"] else "!! "
            print(f"      {m}{scheme}: full-pass {r['fullpass_evaluations']}"
                  f"/{r['expected_fullpass_evaluations']} evals, "
                  f"recovery {r['recovery_evaluations']} evals, "
                  f"recovered {r['recovered_correct']}/{r['recoverable_in_list']}")
            if not r["ok"]:
                bad = [k for k, v in r["checks"].items() if not v]
                print(f"         failed checks: {bad}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
