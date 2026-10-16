"""Fixed cryptographic helpers shared by peers, students and grader.

Everyone derives keys and encrypts/decrypts the SAME documented way, so the MITM
turns on knowing the right shared secret — not on guessing a serialization.

  * shared secret -> bytes: fixed-width big-endian, SECRET_BYTES long.
  * key = HKDF-SHA256(secret_bytes, salt=SHA256(session_id), info=b"infosec-dh-lab-v1")[:32]
  * AES-GCM, 12-byte random nonce, associated data = session_id bytes.
"""
from __future__ import annotations

import base64
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .params import SECRET_BYTES

HKDF_INFO = b"infosec-dh-lab-v1"
NONCE_LEN = 12


def secret_to_bytes(shared_secret: int) -> bytes:
    """Fixed-width big-endian encoding of the integer shared secret."""
    return int(shared_secret).to_bytes(SECRET_BYTES, "big")


def derive_key(shared_secret: int, session_id: str) -> bytes:
    """32-byte AES key via HKDF-SHA256. salt = SHA256(session_id)."""
    salt = hashlib.sha256(session_id.encode("utf-8")).digest()
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=HKDF_INFO)
    return hkdf.derive(secret_to_bytes(shared_secret))


def _aad(session_id: str) -> bytes:
    return session_id.encode("utf-8")


def encrypt(shared_secret: int, session_id: str, plaintext: bytes,
            *, nonce: bytes | None = None) -> dict:
    """Return a packet dict: {session_id, nonce(b64), ciphertext(b64)}.

    Associated data is the session id (bound here, not taken from untrusted
    request fields by the receiver)."""
    import os

    key = derive_key(shared_secret, session_id)
    nonce = nonce or os.urandom(NONCE_LEN)
    ct = AESGCM(key).encrypt(nonce, plaintext, _aad(session_id))
    return {
        "session_id": session_id,
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ct).decode("ascii"),
    }


def decrypt(shared_secret: int, session_id: str, packet: dict) -> bytes:
    """Decrypt a packet; AAD is the documented session_id, not packet-supplied.

    Raises cryptography.exceptions.InvalidTag on tamper / wrong key.
    """
    key = derive_key(shared_secret, session_id)
    nonce = base64.b64decode(packet["nonce"])
    ct = base64.b64decode(packet["ciphertext"])
    return AESGCM(key).decrypt(nonce, ct, _aad(session_id))
