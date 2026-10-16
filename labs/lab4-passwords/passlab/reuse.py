"""Reuse experiment: when is precomputed work reusable across releases?

A lookup table maps digest -> candidate for ONE salt context. Applying it to a
release costs zero new hashing but only hits rows whose salt context matches the
table's. So:

  * an unsalted table reuses across unsalted releases;
  * a shared-salt table reuses only when the shared salt is unchanged;
  * changing the shared salt, or moving to per-row salts, invalidates it and
    forces recomputation (individual salts => per-salt, context-specific work).
"""
from __future__ import annotations

from .candidates import CANDIDATES
from .generator import Fixture, build_fixture, make_assignment, make_release
from .schemes import HashOracle


def build_table(candidates, scheme, salt, *, iterations=None) -> tuple[dict, int]:
    """Precompute {digest: candidate} under one salt context. Returns (table, hashes)."""
    oracle = HashOracle(scheme, iterations)
    table: dict[str, str] = {}
    for c in candidates:
        table[oracle.digest(c, salt)] = c
    return table, oracle.count


def apply_table(table: dict, fixture: Fixture) -> dict:
    """Reuse a table with ZERO new hashing: look up each row's digest."""
    recovered = {}
    for row in fixture.public_rows():
        cand = table.get(row["digest"])
        if cand is not None:
            recovered[row["account_id"]] = cand
    return recovered


def _in_list_count(fixture: Fixture) -> int:
    cands = set(CANDIDATES)
    return sum(1 for pw in fixture.manifest().values() if pw in cands)


def run_reuse_experiment(seed: int = 1) -> dict:
    assignment = make_assignment(seed)

    # Release 1 is a shared-salt (scheme B) table under salt S.
    r1 = make_release(seed, "B", release=1)
    S = r1.shared_salt
    table_S, build_cost = build_table(CANDIDATES, "B", S)

    # Build the four release-2 variants (same assignment, different salting).
    r2_same = build_fixture(assignment, "B", shared_salt=S, release=2)
    r2_changed = make_release(seed, "B", release=2)           # different shared salt
    r2_nosalt = make_release(seed, "A", release=2)            # unsalted
    r2_individual = make_release(seed, "C", release=2)        # per-row salts

    variants = {}
    for name, fx in (("same_shared_salt", r2_same),
                     ("changed_shared_salt", r2_changed),
                     ("no_salt", r2_nosalt),
                     ("new_individual_salts", r2_individual)):
        hits = apply_table(table_S, fx)
        variants[name] = {
            "reused_hits": len(hits),
            "in_list_accounts": _in_list_count(fx),
            "new_hashes_for_reuse": 0,
            "reusable": len(hits) > 0,
        }

    # Cost to actually recover each variant when the table does NOT apply:
    # recompute a per-context table.
    _, recompute_changed = build_table(CANDIDATES, "B", r2_changed.shared_salt)
    distinct_salts_individual = len({a.salt for a in r2_individual.accounts})
    recompute_individual = distinct_salts_individual * len(CANDIDATES)

    # Positive control: an UNSALTED table reuses across unsalted releases.
    table_none, _ = build_table(CANDIDATES, "A", None)
    r2_nosalt_again = make_release(seed, "A", release=3)
    unsalted_reuse = len(apply_table(table_none, r2_nosalt_again))

    return {
        "release1_table": {"scheme": "B", "shared_salt": S, "build_hashes": build_cost},
        "variants": variants,
        "recompute_cost_changed_shared_salt": recompute_changed,
        "individual_salt_distinct_contexts": distinct_salts_individual,
        "recompute_cost_individual_salts": recompute_individual,
        "unsalted_table_reuses_across_unsalted_releases": unsalted_reuse,
        "lesson": ("A shared-salt table is reusable only when that salt matches; "
                   "individual salts require separate, context-specific work."),
    }
