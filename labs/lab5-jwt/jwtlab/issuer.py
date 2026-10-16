"""Token issuer. Holds the private signing key; signs RS256 tokens.

Kept deliberately separate from the verifier and the student repair code: the
grader can run a student's verifier without ever giving it signing authority,
and `issue()` always stamps the account's *real* role — a client cannot request
to be issued an administrator token.
"""
from __future__ import annotations

import time
import uuid

import jwt

from .keys import KeyPair, generate_keypair


class Issuer:
    def __init__(
        self,
        issuer: str,
        audience: str,
        *,
        keypair: KeyPair | None = None,
        lifetime_seconds: int = 3600,
    ) -> None:
        self.issuer = issuer
        self.audience = audience
        self.keypair = keypair or generate_keypair()
        self.lifetime_seconds = lifetime_seconds

    @property
    def public_pem(self) -> bytes:
        return self.keypair.public_pem

    def issue(self, sub: str, role: str, *, lifetime_seconds: int | None = None,
              now: int | None = None) -> str:
        """Issue a signed token for an account. `role` is the account's real,
        server-determined role — callers must not pass a client-chosen value."""
        now = int(now if now is not None else time.time())
        ttl = self.lifetime_seconds if lifetime_seconds is None else lifetime_seconds
        claims = {
            "iss": self.issuer,
            "aud": self.audience,
            "sub": sub,
            "role": role,
            "iat": now,
            "nbf": now,
            "exp": now + ttl,
            "jti": uuid.uuid4().hex,
        }
        return jwt.encode(claims, self.keypair.private_pem, algorithm="RS256")

    # --- helpers used only by tests / graders to build adversarial inputs ---

    def issue_with_wrong_key(self, sub: str, role: str, now: int | None = None) -> str:
        """A token signed by a DIFFERENT RS256 key (attacker's own key)."""
        other = generate_keypair()
        now = int(now if now is not None else time.time())
        claims = {
            "iss": self.issuer, "aud": self.audience, "sub": sub, "role": role,
            "iat": now, "nbf": now, "exp": now + self.lifetime_seconds,
        }
        return jwt.encode(claims, other.private_pem, algorithm="RS256")
