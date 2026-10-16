"""STUDENT TASK — implement the MITM attack.

Write `run_attack(api)` so that Bob ends up receiving Alice's message with
`recipient` changed to "lab-account-B" and `amount` changed to 900, while the
`session_id` and the (initially unknown) `memo` are preserved.

`api` has these methods (both the notebook LabClient and the grader provide them):
    api.create_session()                 -> {session_id, A, B, params, required_change}
    api.substitute(sid, to_alice, to_bob)-> {alice_packet: {session_id, nonce, ciphertext}}
    api.deliver(sid, packet)             -> {receipt_id, delivered}

You have helpers from student.client:
    P, G, Q, is_valid_public, modexp, derive_key, encrypt, decrypt

Plan:
  1. Create a session; read A (Alice's public), B (Bob's public) and p, g.
  2. Pick your OWN fresh private exponents x and y in [2, Q-1] (use `secrets`).
     Send g^x to Alice and g^y to Bob via api.substitute(...). That returns
     Alice's encrypted packet.
  3. Your shared secret with Alice is A^x mod p; with Bob it is B^y mod p.
     Derive keys with the helpers (same documented function the peers use).
  4. Decrypt Alice's packet, change `recipient` and `amount`, keep the rest,
     re-encrypt under your Bob-side key, and deliver it.
  5. Return a dict including the receipt id and the session id.

Do NOT fabricate the memo — you must decrypt Alice's packet to learn it.
"""
from __future__ import annotations

import secrets  # noqa: F401

from student.client import (  # noqa: F401
    P, Q, decrypt, encrypt, is_valid_public, modexp,
)


def run_attack(api) -> dict:
    """TODO(student): implement the active MITM. Return at least
    {"session_id": ..., "receipt_id": ...}."""
    raise NotImplementedError("implement run_attack in attack_stub.py")
