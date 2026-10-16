"""dhlab — shared library for Lab 3 (unauthenticated DH MITM with alteration).

Modules:
    params   RFC 3526 MODP group 14 (p, g=2, q=(p-1)/2) + public-value validation.
    crypto   fixed serialization, HKDF-SHA256 key derivation, AES-GCM helpers.
    peers    Alice/Bob session state, leg establishment, Bob's receive/validate.
    service  Flask app exposing the interception API.

Students get `params` and `crypto` (via student/client.py) but never the peers'
private exponents, the expected plaintext, or the derived keys.
"""
