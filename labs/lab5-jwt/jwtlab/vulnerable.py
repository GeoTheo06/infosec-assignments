"""The intentionally broken verifier shipped with the lab server.

This is *application misuse* of a supported library, not a vulnerable library
version: it calls PyJWT's unverified-decode mode and hands the resulting claims
straight to the authorization logic. The signature, issuer, audience and expiry
are never checked, so anyone can edit `role`/`sub` and be "authenticated".

Students replace this with a correct `verify_token` (see student/verifier_repair.py).
The function signature is identical so the two are drop-in interchangeable.
"""
from __future__ import annotations

import jwt


def verify_token(token: str, public_key: bytes, expected_issuer: str,
                 expected_audience: str) -> dict:
    # BROKEN: signature verification disabled; issuer/audience/expiry ignored.
    # See https://pyjwt.readthedocs.io/en/latest/usage.html#reading-the-claimset-without-validation
    claims = jwt.decode(token, options={"verify_signature": False})
    return claims
