"""Bonus scaffolding: lookup tables vs genuine rainbow tables.

We provide the small, closed password domain, SHA-256, the deterministic
position-dependent reduction function, the chain walk, counters and coverage
helpers. Students implement the table construction and the lookup/verify
(see student/bonus_stub.py); the TA reference is bonus/reference.py.

Domain: 1024 synthetic words, fixed order `P`.
Reduction: R_i(h) = P[(int(h) + i) mod len(P)]  (position-dependent).
A chain of length L walks: p_{j+1} = R_j(SHA256(p_j)), for j in 0..L-1.

Storing every digest/candidate pair is a LOOKUP TABLE. A rainbow table stores
only chain starts and endpoints, trading storage for recomputation at lookup.
Reference: Oechslin, CRYPTO 2003.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

DOMAIN_SIZE = 1024
_STEMS = [
    "alpha", "bravo", "cedar", "delta", "ember", "flint", "grove", "hazel",
    "ivory", "joust", "koala", "larch", "maple", "noble", "ochre", "poppy",
]


def _build_domain() -> list[str]:
    out = []
    i = 0
    while len(out) < DOMAIN_SIZE:
        out.append(f"{_STEMS[i % len(_STEMS)]}{i // len(_STEMS):03d}")
        i += 1
    assert len(set(out)) == DOMAIN_SIZE
    return out


P: list[str] = _build_domain()
_N = len(P)


@dataclass
class Counter:
    hashes: int = 0

    def reset(self) -> None:
        self.hashes = 0


def hash_hex(password: str, counter: Counter | None = None) -> str:
    if counter is not None:
        counter.hashes += 1
    return hashlib.sha256(password.encode("ascii")).hexdigest()


def reduce_fn(h_hex: str, i: int) -> str:
    """Position-dependent reduction: map a digest to a domain password."""
    return P[(int(h_hex, 16) + i) % _N]


def walk_chain(start: str, chain_length: int, counter: Counter | None = None) -> str:
    """Return the endpoint of the chain of `chain_length` steps from `start`."""
    p = start
    for j in range(chain_length):
        p = reduce_fn(hash_hex(p, counter), j)
    return p


def covered_passwords(starts, chain_length: int) -> set[str]:
    """All domain passwords that appear in any column of the chains (ground
    truth for building covered/uncovered test targets)."""
    covered: set[str] = set()
    for s in starts:
        p = s
        for j in range(chain_length):
            covered.add(p)
            p = reduce_fn(hash_hex(p), j)
    return covered


def build_full_lookup_table(counter: Counter | None = None) -> dict:
    """The exhaustive digest->password map (a LOOKUP table, not a rainbow table)."""
    return {hash_hex(w, counter): w for w in P}
