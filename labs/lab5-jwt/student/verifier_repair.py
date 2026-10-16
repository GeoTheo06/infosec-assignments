"""STUDENT REPAIR TASK.

Implement `verify_token` so that it fully validates an RS256 JWT issued by the
lab's trusted issuer, and raises on anything invalid. Then run:

    python -m grader.grade --verifier student.verifier_repair

from the lab root (labs/lab5-jwt) to grade your repair, or point the server at
it:

    JWTLAB_VERIFIER=student.verifier_repair python app/server.py

Your function must:
  * Verify the RS256 signature using `public_key` (PEM bytes you are given).
  * Pin the allowed algorithm to RS256 ONLY. Never trust the token header's
    `alg` to choose the algorithm. (This blocks `alg: none` and algorithm
    confusion.)  See the PyJWT security note:
    https://pyjwt.readthedocs.io/en/latest/usage.html
  * Require and check the issuer == expected_issuer and audience == expected_audience.
  * Require the claims: iss, aud, sub, role, exp.
  * Reject expired tokens (exp in the past).
  * Reject tokens whose `role` is not one of {"student", "admin"} or whose
    `sub` is not a string (clean rejection, not a crash).
  * Return the validated claims dict on success.
  * Raise `jwt.InvalidTokenError` (or a subclass) on ANY validation failure.
    Do NOT return partial/unverified claims.

You are given the surrounding application, key loading, exception handling and
the authorization logic. You only implement validation — not RSA or JSON
parsing from scratch. Use PyJWT (`import jwt`).

NOTE: Do not implement authorization here (role→permission, group membership).
That lives in jwtlab/authz.py and is graded separately. Your job is to decide
whether the token is *authentic and valid*, and to return its claims.
"""
from __future__ import annotations

import jwt  # noqa: F401  (you will use jwt.decode / jwt.InvalidTokenError)

ALLOWED_ROLES = {"student", "admin"}


def verify_token(token: str, public_key: bytes, expected_issuer: str,
                 expected_audience: str) -> dict:
    """Return validated claims or raise jwt.InvalidTokenError.

    TODO(student): implement this. The current stub rejects everything, which
    is *insecure in the wrong direction* — it will fail the legitimate-token
    acceptance checks until you implement real validation.
    """
    raise jwt.InvalidTokenError("verify_token not implemented yet")
