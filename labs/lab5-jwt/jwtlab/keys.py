"""RSA key handling for the JWT lab.

A fresh 2048-bit RSA keypair is generated per issuer instance. The private key
never leaves the issuer process / TA material; students receive only the public
(verification) key in PEM form.
"""
from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@dataclass(frozen=True)
class KeyPair:
    private_pem: bytes
    public_pem: bytes


def generate_keypair(key_size: int = 2048) -> KeyPair:
    key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return KeyPair(private_pem=private_pem, public_pem=public_pem)
