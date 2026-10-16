"""TA REFERENCE repaired verifier. Do not ship to students.

Correct RS256 validation using PyJWT with the algorithm pinned server-side,
issuer/audience/expiry enforced, required claims present, and claim types/role
sanity-checked. Returns validated claims or raises jwt.InvalidTokenError.
"""
from __future__ import annotations

import jwt

ALLOWED_ROLES = {"student", "admin"}
REQUIRED_CLAIMS = ("iss", "aud", "sub", "role", "exp")


def verify_token(token: str, public_key: bytes, expected_issuer: str,
                 expected_audience: str) -> dict:
    try:
        claims = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],          # pinned; never read alg from the header
            issuer=expected_issuer,
            audience=expected_audience,
            options={
                "require": list(REQUIRED_CLAIMS),
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
            },
        )
    except jwt.InvalidTokenError:
        raise
    except Exception as exc:  # malformed token, bad key material, etc.
        raise jwt.InvalidTokenError(f"decode failed: {exc}") from exc

    # Claim-type / value sanity (clean rejection, not a crash downstream).
    sub = claims.get("sub")
    role = claims.get("role")
    if not isinstance(sub, str) or not sub:
        raise jwt.InvalidTokenError("invalid 'sub'")
    if role not in ALLOWED_ROLES:
        raise jwt.InvalidTokenError("invalid 'role'")
    return claims
