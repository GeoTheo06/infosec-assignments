#!/usr/bin/env python3
"""Grader for the Lab 4 bonus (lookup table vs rainbow table).

Grades correctness, stored entries, recomputation and a reuse observation —
not 100% coverage (chains merge, coverage is partial).

Usage (from labs/lab4-passwords):
    python -m bonus.grade --module bonus.reference
    python -m bonus.grade --module student.bonus_stub
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_ROOT))

from bonus.rainbow import (  # noqa: E402
    Counter, P, build_full_lookup_table, covered_passwords, hash_hex,
)

N_STARTS = 128
CHAIN_LENGTH = 8


def grade(module) -> dict:
    build = module.build_rainbow_table
    lookup = module.rainbow_lookup

    starts = P[:N_STARTS]
    counter = Counter()
    table = build(starts, CHAIN_LENGTH, counter)
    build_hashes = counter.hashes
    stored_entries = sum(len(v) for v in table.values())

    covered = covered_passwords(starts, CHAIN_LENGTH)
    uncovered = [w for w in P if w not in covered]

    # Guaranteed-covered targets and some uncovered ones.
    covered_targets = list(covered)[:20]
    uncovered_targets = uncovered[:20]

    # Correctness + coverage on covered targets.
    recovered_covered = 0
    false_positive = 0
    lookup_hashes = 0
    for pw in covered_targets:
        c = Counter()
        got = lookup(hash_hex(pw), table, CHAIN_LENGTH, c)
        lookup_hashes += c.hashes
        if got is not None:
            if hash_hex(got) == hash_hex(pw):
                recovered_covered += 1
            else:
                false_positive += 1

    # Any password returned for an uncovered target must still verify.
    for pw in uncovered_targets:
        got = lookup(hash_hex(pw), table, CHAIN_LENGTH)
        if got is not None and hash_hex(got) != hash_hex(pw):
            false_positive += 1

    # Storage comparison vs the exhaustive lookup table.
    full = build_full_lookup_table()
    full_entries = len(full)

    # Reuse observation: a table built for UNSALTED digests does not recover a
    # SALTED target (H(pw||salt)); individual salts need separate work.
    salt = "deadbeef" * 4  # 32 hex chars
    salted_target = hash_hex("alpha000" + salt)
    salted_hit = lookup(salted_target, table, CHAIN_LENGTH)
    salt_reuse_fails = salted_hit is None or hash_hex(salted_hit) != salted_target

    checks = {
        "covered_targets_mostly_recovered": recovered_covered >= 0.9 * len(covered_targets),
        "no_false_positives": false_positive == 0,
        "rainbow_smaller_than_full_lookup": stored_entries < full_entries,
        "salt_reuse_requires_new_work": salt_reuse_fails,
    }
    return {
        "params": {"starts": N_STARTS, "chain_length": CHAIN_LENGTH},
        "stored_entries_rainbow": stored_entries,
        "stored_entries_full_lookup": full_entries,
        "build_hashes": build_hashes,
        "covered_domain": len(covered),
        "covered_targets": len(covered_targets),
        "recovered_covered": recovered_covered,
        "false_positives": false_positive,
        "lookup_hashes_total": lookup_hashes,
        "checks": checks,
        "ok": all(checks.values()),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lab 4 bonus grader")
    ap.add_argument("--module", required=True,
                    help="dotted module exposing build_rainbow_table + rainbow_lookup")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        mod = importlib.import_module(args.module)
        report = grade(mod)
    except NotImplementedError as exc:
        report = {"ok": False, "error": f"not implemented: {exc}"}
    except Exception as exc:
        report = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    if args.json:
        import json
        print(json.dumps(report, indent=2))
        return 0 if report.get("ok") else 1

    print(f"Lab 4 bonus grader ({args.module}) — {'PASS' if report.get('ok') else 'FAIL'}")
    if report.get("error"):
        print(f"  {report['error']}")
        return 1
    print(f"  rainbow stored entries: {report['stored_entries_rainbow']} "
          f"vs full lookup: {report['stored_entries_full_lookup']}")
    print(f"  covered domain: {report['covered_domain']}/1024; "
          f"recovered {report['recovered_covered']}/{report['covered_targets']} covered targets")
    print(f"  build hashes: {report['build_hashes']}; "
          f"lookup hashes (sum): {report['lookup_hashes_total']}; "
          f"false positives: {report['false_positives']}")
    if not report["ok"]:
        print(f"  failed checks: {[k for k,v in report['checks'].items() if not v]}")
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
