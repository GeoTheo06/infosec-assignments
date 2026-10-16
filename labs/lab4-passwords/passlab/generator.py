"""Seeded fixture generator for the password benchmark.

Produces database "releases" for schemes A–D. The account/password *assignment*
is shared across A, B and C (so comparisons are apples-to-apples); only the
salting differs. Salts are regenerated per release without changing difficulty.

Public rows (what students see): account_id, scheme, salt, iterations, digest.
The answer manifest (account_id -> password) is PRIVATE (TA/grader only).
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field

from . import schemes
from .candidates import ABSENT_PASSWORDS, CANDIDATES

N_ACCOUNTS = 12


@dataclass
class Account:
    account_id: str
    password: str          # PRIVATE
    salt: str | None
    digest: str


@dataclass
class Fixture:
    scheme: str
    accounts: list[Account]
    shared_salt: str | None = None
    iterations: int | None = None
    release: int = 1
    meta: dict = field(default_factory=dict)

    def public_rows(self) -> list[dict]:
        rows = []
        for a in self.accounts:
            row = {"account_id": a.account_id, "scheme": self.scheme,
                   "salt": a.salt, "digest": a.digest}
            if self.iterations is not None:
                row["iterations"] = self.iterations
            rows.append(row)
        return rows

    def manifest(self) -> dict:
        return {a.account_id: a.password for a in self.accounts}

    def public_json(self) -> str:
        return json.dumps({
            "scheme": self.scheme, "release": self.release,
            "iterations": self.iterations, "shared_salt": self.shared_salt,
            "rows": self.public_rows(),
        }, indent=2)


def _salt(rng: random.Random) -> str:
    """32-char ASCII hex salt from 16 random bytes."""
    return rng.getrandbits(128).to_bytes(16, "big").hex()


def make_assignment(seed: int, n_accounts: int = N_ACCOUNTS) -> list[tuple[str, str]]:
    """Deterministic (account_id, password) list shared across schemes A–C.

    Guarantees: some passwords repeat across accounts; a few passwords are NOT
    in the candidate list (so they stay unrecovered in a bounded attack)."""
    rng = random.Random(f"assign:{seed}")
    pool = rng.sample(CANDIDATES, k=8)        # bounded pool -> forces repeats
    passwords = [rng.choice(pool) for _ in range(n_accounts)]
    # Force explicit duplicates and inject absent passwords at fixed-ish slots.
    passwords[1] = passwords[0]               # guaranteed repeat
    absent_slots = rng.sample(range(n_accounts), k=len(ABSENT_PASSWORDS))
    for slot, pw in zip(absent_slots, ABSENT_PASSWORDS):
        passwords[slot] = pw
    return [(f"acct-{i:02d}", passwords[i]) for i in range(n_accounts)]


def build_fixture(assignment: list[tuple[str, str]], scheme: str, *,
                  shared_salt: str | None = None,
                  salts: list[str] | None = None,
                  iterations: int | None = None, release: int = 1) -> Fixture:
    """Build a fixture from an explicit assignment and salting choice."""
    accounts: list[Account] = []
    for i, (aid, pw) in enumerate(assignment):
        if scheme == "A":
            salt = None
        elif scheme == "B":
            salt = shared_salt
        else:  # C or D -> per-row salt
            salt = salts[i]
        digest = schemes.compute(scheme, pw, salt, iterations)
        accounts.append(Account(aid, pw, salt, digest))
    return Fixture(scheme=scheme, accounts=accounts, shared_salt=shared_salt,
                   iterations=iterations, release=release)


def make_release(seed: int, scheme: str, *, release: int = 1,
                 iterations: int | None = None) -> Fixture:
    """Convenience: deterministic salts derived from (seed, scheme, release)."""
    assignment = make_assignment(seed)
    srng = random.Random(f"salt:{seed}:{scheme}:{release}")
    shared_salt = _salt(srng) if scheme == "B" else None
    salts = [_salt(srng) for _ in assignment] if scheme in ("C", "D") else None
    if scheme == "D" and iterations is None:
        iterations = 50_000
    return build_fixture(assignment, scheme, shared_salt=shared_salt,
                         salts=salts, iterations=iterations, release=release)


# --- scheme D small paired benchmark (2 accounts, 128 candidates) ------------

D_ACCOUNTS = 2
D_CANDIDATES = 128


def d_candidates() -> list[str]:
    return CANDIDATES[:D_CANDIDATES]


def make_d_release(seed: int, iterations: int, *, release: int = 1) -> Fixture:
    """Small scheme-D fixture: 2 accounts, passwords within the first 128
    candidates, individual salts, a chosen iteration count."""
    rng = random.Random(f"d-assign:{seed}")
    pool = d_candidates()
    assignment = [(f"d-acct-{i:02d}", rng.choice(pool)) for i in range(D_ACCOUNTS)]
    srng = random.Random(f"d-salt:{seed}:{iterations}:{release}")
    salts = [_salt(srng) for _ in assignment]
    return build_fixture(assignment, "D", salts=salts, iterations=iterations,
                         release=release)
