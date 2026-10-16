"""STUDENT BONUS TASK — implement rainbow-table build + lookup.

Primitives are provided in bonus/rainbow.py:
    P            ordered domain (1024 words)
    hash_hex(pw, counter)   SHA-256 hex (counts the hash if a counter is given)
    reduce_fn(h_hex, i)     position-dependent reduction R_i
    walk_chain(start, L, counter)   endpoint of the chain from `start`
    Counter                 .hashes counter

Implement:
    build_rainbow_table(starts, chain_length, counter) -> {endpoint: [starts]}
        Keep duplicate endpoints as multiple possible starts.

    rainbow_lookup(target_digest, table, chain_length, counter) -> password | None
        For each possible column position (high to low), walk from the target to
        an endpoint; if that endpoint is in the table, regenerate each candidate
        chain from its start, hashing forward, and return the first password
        whose hash equals target_digest (verify before returning).

Full coverage is NOT guaranteed (chains merge); grade is on correctness, stored
entries, recomputation and reuse observations — not on 100% recovery.

Grade:
    python -m bonus.grade --module student.bonus_stub
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bonus.rainbow import (  # noqa: E402,F401
    Counter, P, hash_hex, reduce_fn, walk_chain,
)


def build_rainbow_table(starts, chain_length, counter=None) -> dict:
    """TODO(student)."""
    raise NotImplementedError("implement build_rainbow_table")


def rainbow_lookup(target_digest, table, chain_length, counter=None):
    """TODO(student)."""
    raise NotImplementedError("implement rainbow_lookup")
