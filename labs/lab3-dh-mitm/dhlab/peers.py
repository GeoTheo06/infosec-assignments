"""Peer (Alice/Bob) session state and operations.

Keeps all secret state in the service process: private exponents, Alice's
plaintext (with a fresh random memo the attacker cannot guess), and the derived
keys. The interception API exposes only public values and events.
"""
from __future__ import annotations

import json
import secrets
import uuid
from dataclasses import dataclass, field

from cryptography.exceptions import InvalidTag

from . import crypto
from .params import G, P, Q, is_valid_public

RECIPIENT_FROM = "lab-account-A"
RECIPIENT_TO = "lab-account-B"
AMOUNT_FROM = 10
AMOUNT_TO = 900


class SessionError(Exception):
    def __init__(self, status: int, reason: str) -> None:
        super().__init__(reason)
        self.status = status
        self.reason = reason


@dataclass
class Session:
    session_id: str
    a: int                      # Alice private exponent (SECRET)
    b: int                      # Bob private exponent (SECRET)
    A: int                      # Alice public value g^a
    B: int                      # Bob public value g^b
    alice_plaintext: dict       # Alice's real message (SECRET until decrypted)
    to_alice: int | None = None    # public value Alice received (attacker-chosen)
    to_bob: int | None = None      # public value Bob received (attacker-chosen)
    alice_packet: dict | None = None
    bob_received: dict | None = None   # what Bob decrypted (grader-inspectable)
    receipts: list = field(default_factory=list)
    transcript: list = field(default_factory=list)

    # --- public views -------------------------------------------------------
    def required_change(self) -> dict:
        return {
            "recipient": {"from": RECIPIENT_FROM, "to": RECIPIENT_TO},
            "amount": {"from": AMOUNT_FROM, "to": AMOUNT_TO},
            "preserve": ["session_id", "memo"],
            "note": "Change recipient and amount; keep session_id and the "
                    "(unknown until you decrypt) memo unchanged.",
        }

    def public_view(self) -> dict:
        return {
            "session_id": self.session_id,
            "A": str(self.A),
            "B": str(self.B),
            "required_change": self.required_change(),
        }


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def get(self, sid: str) -> Session:
        s = self._sessions.get(sid)
        if s is None:
            raise SessionError(404, "unknown session")
        return s

    def create(self) -> Session:
        sid = uuid.uuid4().hex
        a = secrets.randbelow(Q - 2) + 2
        b = secrets.randbelow(Q - 2) + 2
        A = pow(G, a, P)
        B = pow(G, b, P)
        alice_plaintext = {
            "session_id": sid,
            "recipient": RECIPIENT_FROM,
            "amount": AMOUNT_FROM,
            "memo": "memo-" + secrets.token_hex(8),  # fresh, unknown to attacker
        }
        s = Session(session_id=sid, a=a, b=b, A=A, B=B,
                    alice_plaintext=alice_plaintext)
        s.transcript.append({"event": "created", "A": str(A), "B": str(B)})
        self._sessions[sid] = s
        return s

    def substitute(self, sid: str, to_alice: int, to_bob: int) -> dict:
        """Deliver attacker-chosen public values to Alice and Bob.

        Alice encrypts her message under the key derived from the value SHE
        received (to_alice). Returns Alice's packet. Bob will later decrypt with
        the key derived from the value HE received (to_bob).
        """
        s = self.get(sid)
        for name, v in (("to_alice", to_alice), ("to_bob", to_bob)):
            if not is_valid_public(v):
                raise SessionError(400, f"invalid public value for {name}")
        s.to_alice = to_alice
        s.to_bob = to_bob
        # Alice's shared secret with whoever sent her `to_alice`.
        alice_secret = pow(to_alice, s.a, P)
        plaintext = json.dumps(s.alice_plaintext, separators=(",", ":")).encode()
        s.alice_packet = crypto.encrypt(alice_secret, s.session_id, plaintext)
        s.transcript.append({
            "event": "substituted",
            "to_alice": str(to_alice), "to_bob": str(to_bob),
        })
        s.transcript.append({"event": "alice_sent", "packet": s.alice_packet})
        return s.alice_packet

    def deliver(self, sid: str, packet: dict) -> dict:
        """Bob receives and decrypts the delivered packet.

        Bob's shared secret comes from the value HE received (to_bob). On
        success, records what Bob parsed and returns a receipt id. GCM failures
        (tamper / wrong key) raise 422.
        """
        s = self.get(sid)
        if s.to_bob is None:
            raise SessionError(409, "substitute step not performed")
        bob_secret = pow(s.to_bob, s.b, P)
        try:
            pt = crypto.decrypt(bob_secret, s.session_id, packet)
        except InvalidTag as exc:
            s.transcript.append({"event": "deliver_failed", "reason": "InvalidTag"})
            raise SessionError(422, "GCM verification failed (InvalidTag)") from exc
        except Exception as exc:
            raise SessionError(400, f"malformed packet: {exc}") from exc
        try:
            parsed = json.loads(pt)
        except json.JSONDecodeError as exc:
            raise SessionError(422, "decrypted bytes are not valid JSON") from exc

        receipt_id = "rcpt-" + secrets.token_hex(6)
        s.bob_received = parsed
        s.receipts.append(receipt_id)
        s.transcript.append({"event": "bob_received", "receipt": receipt_id})
        return {"receipt_id": receipt_id, "delivered": True}

    # --- grader-only (private) ---------------------------------------------
    def expected_final_message(self, sid: str) -> dict:
        """The message Bob SHOULD end up with after a correct MITM: target
        fields changed, memo + session_id preserved. TA/grader use only."""
        s = self.get(sid)
        return {
            "session_id": s.session_id,
            "recipient": RECIPIENT_TO,
            "amount": AMOUNT_TO,
            "memo": s.alice_plaintext["memo"],
        }
