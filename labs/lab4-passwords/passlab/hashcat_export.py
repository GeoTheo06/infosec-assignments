"""Export fixtures to Hashcat hash formats (optional cracking-tool practice).

    A -> mode 1400  : sha256($pass)                 -> "<digest>"
    B,C -> mode 1410: sha256($pass.$salt)           -> "<digest>:<salt>"
    D -> mode 10900 : PBKDF2-HMAC-SHA256            -> "sha256:<iter>:<b64 salt>:<b64 dk>"

Our salt is the 32-char hex STRING; its ASCII characters are the salt bytes, so
`$salt` in modes 1410 is exactly that string, and for 10900 we base64 those
ASCII bytes. The scheme-D digest is the 32-byte derived key (we store its hex),
base64-encoded for 10900.

Hashcat example hashes: https://hashcat.net/wiki/doku.php?id=example_hashes
"""
from __future__ import annotations

import base64

from .generator import Fixture

MODES = {"A": 1400, "B": 1410, "C": 1410, "D": 10900}


def _line_for(scheme: str, row: dict) -> str:
    if scheme == "A":
        return row["digest"]
    if scheme in ("B", "C"):
        return f"{row['digest']}:{row['salt']}"
    if scheme == "D":
        salt_b64 = base64.b64encode(row["salt"].encode("ascii")).decode("ascii")
        dk_b64 = base64.b64encode(bytes.fromhex(row["digest"])).decode("ascii")
        return f"sha256:{row['iterations']}:{salt_b64}:{dk_b64}"
    raise ValueError(f"unknown scheme {scheme!r}")


def export_lines(fixture: Fixture) -> list[str]:
    return [_line_for(fixture.scheme, r) for r in fixture.public_rows()]


def export(fixture: Fixture) -> dict:
    return {"mode": MODES[fixture.scheme], "lines": export_lines(fixture)}
