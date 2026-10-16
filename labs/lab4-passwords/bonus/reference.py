"""TA REFERENCE rainbow-table build + lookup. Do not ship.

Builds {endpoint: [starts]} (duplicate endpoints keep multiple starts) and looks
up a target digest by trying each possible column position, walking to an
endpoint, then regenerating candidate chains to find and verify the pre-image.
"""
from __future__ import annotations

from .rainbow import Counter, hash_hex, reduce_fn, walk_chain


def build_rainbow_table(starts, chain_length: int, counter: Counter | None = None) -> dict:
    table: dict[str, list[str]] = {}
    for s in starts:
        endpoint = walk_chain(s, chain_length, counter)
        table.setdefault(endpoint, []).append(s)
    return table


def rainbow_lookup(target_digest: str, table: dict, chain_length: int,
                   counter: Counter | None = None) -> str | None:
    """Return a password whose SHA-256 equals target_digest, or None."""
    for c in range(chain_length - 1, -1, -1):
        # Walk from the target's column c to an endpoint.
        p = reduce_fn(target_digest, c)
        for j in range(c + 1, chain_length):
            p = reduce_fn(hash_hex(p, counter), j)
        endpoint = p
        if endpoint not in table:
            continue
        # Regenerate each candidate chain from its start to find the pre-image.
        for start in table[endpoint]:
            p = start
            for j in range(chain_length):
                h = hash_hex(p, counter)
                if h == target_digest:
                    return p            # verified pre-image
                p = reduce_fn(h, j)
    return None
