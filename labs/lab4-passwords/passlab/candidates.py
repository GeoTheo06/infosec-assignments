"""The fixed-order candidate password list.

A deterministic, fixed-order list of 512 distinct ASCII candidate passwords.
Account passwords are drawn mostly from this list; a few accounts use passwords
that are deliberately NOT in it (those stay unrecovered in a bounded attack).

The list is content-addressed by SHA-256 so a release can pin the exact order.
"""
from __future__ import annotations

import hashlib

CANDIDATE_COUNT = 512

# A small set of readable stems combined deterministically into 512 entries.
_STEMS = [
    "sunset", "orange", "guitar", "planet", "silver", "forest", "rocket",
    "velvet", "copper", "meadow", "falcon", "dragon", "harbor", "pepper",
    "cactus", "violet", "pirate", "tunnel", "ginger", "mellow", "walnut",
    "quartz", "lagoon", "cobalt", "tangle", "pigeon", "saddle", "mosaic",
    "cipher", "nugget", "bramble", "zephyr",
]


def _build() -> list[str]:
    out: list[str] = []
    i = 0
    while len(out) < CANDIDATE_COUNT:
        stem = _STEMS[i % len(_STEMS)]
        num = i // len(_STEMS)
        out.append(f"{stem}{num:02d}")
        i += 1
    assert len(set(out)) == CANDIDATE_COUNT, "candidates must be distinct"
    return out


CANDIDATES: list[str] = _build()


def candidates_sha256() -> str:
    joined = "\n".join(CANDIDATES).encode("ascii")
    return hashlib.sha256(joined).hexdigest()


# Passwords used by accounts but intentionally absent from the list above, so a
# bounded attack cannot recover them.
ABSENT_PASSWORDS = [
    "notinthelist-aa",
    "notintheList-bb",
    "9f3x-outside-cc",
]
