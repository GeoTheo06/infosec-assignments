"""TA REFERENCE active MITM attack (two attacker exponents). Do not ship.

Uses valid public values and two fresh attacker exponents x, y — NOT the
parameter-injection/key-fixing shortcut. Alice shares a key with the attacker;
Bob shares a different key with the attacker.
"""
from __future__ import annotations

import json
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dhlab.crypto import decrypt, encrypt   # noqa: E402
from dhlab.params import G, P, Q            # noqa: E402


def run_attack(api) -> dict:
    sess = api.create_session()
    sid = sess["session_id"]
    A = int(sess["A"])
    B = int(sess["B"])
    p = int(sess["params"]["p"])
    g = int(sess["params"]["g"])

    # Two fresh attacker private exponents.
    x = secrets.randbelow(Q - 2) + 2
    y = secrets.randbelow(Q - 2) + 2
    to_alice = pow(g, x, p)   # g^x -> Alice
    to_bob = pow(g, y, p)     # g^y -> Bob

    resp = api.substitute(sid, to_alice, to_bob)
    alice_packet = resp["alice_packet"]

    # Legs: secret with Alice = A^x ; secret with Bob = B^y.
    secret_with_alice = pow(A, x, p)
    secret_with_bob = pow(B, y, p)

    # Recover Alice's full plaintext (we must, to keep the unknown memo).
    plaintext = decrypt(secret_with_alice, sid, alice_packet)
    message = json.loads(plaintext)

    # Make the specified changes; preserve everything else (session_id, memo).
    message["recipient"] = "lab-account-B"
    message["amount"] = 900

    # Re-encrypt under Bob's key and deliver.
    new_packet = encrypt(
        secret_with_bob, sid,
        json.dumps(message, separators=(",", ":")).encode(),
    )
    receipt = api.deliver(sid, new_packet)

    return {
        "session_id": sid,
        "receipt_id": receipt["receipt_id"],
        "recovered_memo": message["memo"],
        "sent_message": message,
    }
