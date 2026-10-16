"""Instrumented recovery runner.

The runner owns the counted HashOracle, invokes a recovery *strategy*, validates
the result against the private manifest, and reports authoritative work counts.
Students implement the strategy; the runner (trusted) measures it.

Two modes:
  * recovery   — the strategy may stop early once a salt group is fully solved.
  * full_pass  — the strategy evaluates every candidate for every distinct salt
                 context, giving stable, early-stop-independent counts.
"""
from __future__ import annotations

from .candidates import CANDIDATES
from .generator import Fixture, d_candidates
from .schemes import HashOracle


def group_by_salt(rows: list[dict]) -> dict:
    """Group public rows by their salt context (None for unsalted).

    Grouping is the whole point: each candidate need only be hashed ONCE per
    distinct salt, not once per account."""
    groups: dict = {}
    for row in rows:
        groups.setdefault(row.get("salt"), []).append(row)
    return groups


def distinct_salt_count(rows: list[dict]) -> int:
    return len(group_by_salt(rows))


def candidates_for(fixture: Fixture) -> list[str]:
    return d_candidates() if fixture.scheme == "D" else CANDIDATES


def run(fixture: Fixture, strategy, *, full_pass: bool,
        candidates: list[str] | None = None) -> dict:
    """Run a strategy against a fixture and return an authoritative report."""
    oracle = HashOracle(fixture.scheme, fixture.iterations)
    rows = fixture.public_rows()
    cands = candidates if candidates is not None else candidates_for(fixture)

    recovered = strategy(rows, cands, oracle, full_pass=full_pass) or {}

    manifest = fixture.manifest()
    correct = {aid: pw for aid, pw in recovered.items()
               if isinstance(pw, str) and manifest.get(aid) == pw}
    wrong = {aid: pw for aid, pw in recovered.items() if aid not in correct}

    # Accounts whose password is not in the candidate list cannot be recovered.
    in_list = {aid for aid, pw in manifest.items() if pw in set(cands)}
    recoverable = len(in_list)

    return {
        "scheme": fixture.scheme,
        "release": fixture.release,
        "mode": "full_pass" if full_pass else "recovery",
        "iterations": fixture.iterations,
        "accounts": len(rows),
        "distinct_salts": distinct_salt_count(rows),
        "candidates": len(cands),
        "evaluations": oracle.count,
        "recovered_correct": len(correct),
        "recovered_wrong": len(wrong),
        "recoverable_in_list": recoverable,
        "correct": correct,
        "wrong": wrong,
    }
