"""The four storage schemes and a counted hash oracle.

| Scheme | Construction                                                   |
|--------|----------------------------------------------------------------|
| A      | SHA256(password_bytes)                                         |
| B      | SHA256(password_bytes || salt_bytes), one shared salt for all |
| C      | SHA256(password_bytes || salt_bytes), a salt per row          |
| D      | PBKDF2-HMAC-SHA256(password, salt, iterations, dklen=32)      |

`salt` is the 32-char ASCII hex STRING; its displayed characters are hashed
directly (we do NOT hex-decode it). Passwords are ASCII.
"""
from __future__ import annotations

import hashlib

SCHEMES = ("A", "B", "C", "D")
DKLEN = 32


def _pw_bytes(password: str) -> bytes:
    return password.encode("ascii")


def _salt_bytes(salt: str | None) -> bytes:
    # The *displayed* hex characters are the salt bytes (not hex-decoded).
    return b"" if salt is None else salt.encode("ascii")


def digest_A(password: str) -> str:
    return hashlib.sha256(_pw_bytes(password)).hexdigest()


def digest_B(password: str, salt: str) -> str:
    return hashlib.sha256(_pw_bytes(password) + _salt_bytes(salt)).hexdigest()


# C uses the same construction as B (per-row salt).
digest_C = digest_B


def digest_D(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", _pw_bytes(password), _salt_bytes(salt), iterations, dklen=DKLEN
    ).hex()


def compute(scheme: str, password: str, salt: str | None = None,
            iterations: int | None = None) -> str:
    if scheme == "A":
        return digest_A(password)
    if scheme in ("B", "C"):
        if salt is None:
            raise ValueError(f"scheme {scheme} requires a salt")
        return digest_B(password, salt)
    if scheme == "D":
        if salt is None or iterations is None:
            raise ValueError("scheme D requires salt and iterations")
        return digest_D(password, salt, iterations)
    raise ValueError(f"unknown scheme {scheme!r}")


class HashOracle:
    """Counts every digest evaluation. The runner/grader own the oracle so work
    counts are authoritative (students cannot self-report a lower count)."""

    def __init__(self, scheme: str, iterations: int | None = None) -> None:
        self.scheme = scheme
        self.iterations = iterations
        self.count = 0

    def digest(self, password: str, salt: str | None = None) -> str:
        self.count += 1
        return compute(self.scheme, password, salt, self.iterations)

    def reset(self) -> None:
        self.count = 0
