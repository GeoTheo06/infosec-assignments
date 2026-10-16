"""TA REFERENCE recovery strategy. Do not ship.

Groups targets by salt so each candidate is hashed once per distinct salt
context. In recovery mode it stops hashing a group once every target digest in
that group has been found; in full_pass mode it evaluates every candidate for
every group (stable counts: A=512, B=512, C=6144 for 512 candidates).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from passlab.runner import group_by_salt   # noqa: E402


def recover(rows, candidates, oracle, full_pass=False) -> dict:
    recovered: dict[str, str] = {}
    for salt, group_rows in group_by_salt(rows).items():
        want: dict[str, list[str]] = {}
        for r in group_rows:
            want.setdefault(r["digest"], []).append(r["account_id"])
        remaining = set(want)
        for cand in candidates:
            d = oracle.digest(cand, salt)
            if d in want:
                for aid in want[d]:
                    recovered[aid] = cand
                remaining.discard(d)
                if not full_pass and not remaining:
                    break
    return recovered
