"""Fixed DH parameters: RFC 3526, section 3 — 2048-bit MODP group 14.

generator g = 2, q = (p - 1) / 2. For this group, 2 generates the order-q
subgroup of quadratic residues, so honest public values g^a satisfy
pow(value, q, p) == 1 and the subgroup-membership check below is exact.
"""
from __future__ import annotations

# RFC 3526 group 14 prime (hex, whitespace stripped at import).
_P_HEX = """
FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D
C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F
83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D
670C354E 4ABC9804 F1746C08 CA18217C 32905E46 2E36CE3B
E39E772C 180E8603 9B2783A2 EC07A28F B5C55DF0 6F4C52C9
DE2BCBF6 95581718 3995497C EA956AE5 15D22618 98FA0510
15728E5A 8AACAA68 FFFFFFFF FFFFFFFF
"""

P = int(_P_HEX.replace("\n", "").replace(" ", ""), 16)
G = 2
Q = (P - 1) // 2
# Byte width used for the fixed-width shared-secret serialization.
SECRET_BYTES = 256  # 2048 bits


def is_valid_public(value: int) -> bool:
    """Reject trivial/invalid values and require order-q subgroup membership.

    Excludes 0, 1 and p-1 (the small-order / trivial values) and requires
    value^q == 1 (mod p), i.e. membership in the prime-order-q subgroup. This
    keeps the exercise about missing authentication, not weak parameters.
    """
    if not isinstance(value, int):
        return False
    if value <= 1 or value >= P - 1:
        return False
    return pow(value, Q, P) == 1


def params_public() -> dict:
    """Public parameter description returned by the API (decimal strings)."""
    return {
        "group": "RFC3526-MODP-2048-group14",
        "p": str(P),
        "g": G,
        "q": str(Q),
        "secret_bytes": SECRET_BYTES,
    }
