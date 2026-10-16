#!/usr/bin/env python3
"""Integration grader for Lab 5 (JWT).

Imports a submitted verifier, wires it into the real app with a FRESH issuer
(fresh RSA keys), fresh accounts and freshly minted claims, then runs the
acceptance-test matrix from the brief against real endpoint behavior. It
distinguishes 401 (invalid authentication) from 403 (valid auth, insufficient
permission).

Usage (from labs/lab5-jwt):
    python -m grader.grade --verifier ta.verifier_solution
    python -m grader.grade --verifier student.verifier_repair
    python -m grader.grade --verifier path/to/some_verifier.py
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import importlib
import importlib.util
import json
import sys
import time
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_ROOT))

import jwt  # noqa: E402

from jwtlab.app import create_app          # noqa: E402
from jwtlab.authz import default_store      # noqa: E402
from jwtlab.issuer import Issuer            # noqa: E402
from student.token_editor import make_alg_none, tamper  # noqa: E402

ISS = "https://issuer.infosec-lab.example/"
AUD = "infosec-lab"


def _load_verifier(spec: str):
    """Load verify_token from a dotted module path or a .py file path."""
    if spec.endswith(".py"):
        path = Path(spec).resolve()
        modspec = importlib.util.spec_from_file_location("submitted_verifier", path)
        mod = importlib.util.module_from_spec(modspec)
        modspec.loader.exec_module(mod)  # type: ignore[union-attr]
    else:
        mod = importlib.import_module(spec)
    return getattr(mod, "verify_token")


def _raw_sign(issuer: Issuer, claims: dict, *, alg: str = "RS256", key=None) -> str:
    """TA-side signer to mint adversarial-but-signed tokens."""
    return jwt.encode(claims, key or issuer.keypair.private_pem, algorithm=alg)


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _hs256_confusion(claims: dict, public_pem: bytes) -> str:
    """Hand-craft the classic RS256->HS256 confusion token: HMAC-SHA256 over
    header.payload using the RSA *public* key bytes as the HMAC secret. PyJWT
    refuses to encode this (good), so we build it manually. A verifier pinned to
    RS256 must reject it on the algorithm, not try to HMAC-verify it."""
    header = {"alg": "HS256", "typ": "JWT"}
    h = _b64url(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url(json.dumps(claims, separators=(",", ":")).encode())
    signing_input = f"{h}.{p}".encode("ascii")
    sig = hmac.new(public_pem, signing_input, hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url(sig)}"


def build_cases(issuer: Issuer):
    """Return a list of (name, token, method, path, expected_status, note)."""
    now = int(time.time())
    base = {"iss": ISS, "aud": AUD, "exp": now + 3600, "iat": now, "nbf": now}

    student_tok = issuer.issue("alice", "student")
    admin_tok = issuer.issue("root", "admin")

    cases = []

    # 1. Genuine ordinary-user token: whoami OK, admin forbidden (403).
    cases.append(("genuine_student_whoami", student_tok, "GET", "/whoami", 200,
                  "ordinary user authenticates"))
    cases.append(("genuine_student_admin_forbidden", student_tok, "GET",
                  "/admin/marker", 403, "student must not reach admin op"))

    # 2. Genuine admin token from trusted issuer: admin op succeeds.
    cases.append(("genuine_admin_ok", admin_tok, "GET", "/admin/marker", 200,
                  "admin succeeds"))

    # 3. Changed role / subject with the original signature -> 401.
    cases.append(("tampered_role_admin", tamper(student_tok, {"role": "admin"}),
                  "GET", "/admin/marker", 401, "role escalation via edit"))
    cases.append(("tampered_sub_root", tamper(student_tok, {"sub": "root", "role": "admin"}),
                  "GET", "/admin/marker", 401, "identity swap via edit"))

    # 4. Corrupted signature / wrong signing key -> 401.
    corrupt = student_tok[:-3] + ("AAA" if not student_tok.endswith("AAA") else "BBB")
    cases.append(("corrupted_signature", corrupt, "GET", "/whoami", 401,
                  "garbled signature"))
    cases.append(("wrong_signing_key", issuer.issue_with_wrong_key("root", "admin"),
                  "GET", "/admin/marker", 401, "signed by attacker's own RSA key"))

    # 5. Unsigned token / unapproved algorithm -> 401.
    cases.append(("alg_none", make_alg_none(student_tok, {"role": "admin"}),
                  "GET", "/admin/marker", 401, "alg:none unsigned"))
    hs_tok = _hs256_confusion({**base, "sub": "root", "role": "admin"},
                              issuer.public_pem)
    cases.append(("alg_confusion_hs256", hs_tok, "GET", "/admin/marker", 401,
                  "HS256 using the public key as secret"))

    # 6. Expired token -> 401.
    expired = _raw_sign(issuer, {"iss": ISS, "aud": AUD, "sub": "root",
                                 "role": "admin", "iat": now - 7200,
                                 "nbf": now - 7200, "exp": now - 3600})
    cases.append(("expired", expired, "GET", "/admin/marker", 401, "exp in the past"))

    # 7. Missing required claim / wrong issuer or audience -> 401.
    no_exp = _raw_sign(issuer, {"iss": ISS, "aud": AUD, "sub": "root", "role": "admin"})
    cases.append(("missing_exp", no_exp, "GET", "/admin/marker", 401, "no exp claim"))
    wrong_iss = _raw_sign(issuer, {**base, "iss": "https://evil.example/",
                                   "sub": "root", "role": "admin"})
    cases.append(("wrong_issuer", wrong_iss, "GET", "/admin/marker", 401, "bad iss"))
    wrong_aud = _raw_sign(issuer, {**base, "aud": "other-app", "sub": "root",
                                   "role": "admin"})
    cases.append(("wrong_audience", wrong_aud, "GET", "/admin/marker", 401, "bad aud"))

    # 8. Malformed token / invalid claim types or role -> 401 (clean).
    cases.append(("malformed", "not.a.valid.jwt", "GET", "/whoami", 401,
                  "garbage input"))
    bad_role = _raw_sign(issuer, {**base, "sub": "root", "role": "superuser"})
    cases.append(("invalid_role_value", bad_role, "GET", "/admin/marker", 401,
                  "role not in allowed set"))
    bad_sub = _raw_sign(issuer, {**base, "sub": 1234, "role": "admin"})
    cases.append(("invalid_sub_type", bad_sub, "GET", "/admin/marker", 401,
                  "sub is not a string"))

    # 9. Valid token for an unknown / other-group account -> 403 (no access).
    ghost = issuer.issue("ghost", "admin")   # validly signed, not in this group
    cases.append(("valid_unknown_account", ghost, "GET", "/admin/marker", 403,
                  "authenticates but account not in group"))

    return cases


def run_matrix(verify_token) -> dict:
    issuer = Issuer(ISS, AUD, lifetime_seconds=3600)
    store = default_store(group="group-01", run_id="run-grader")
    app = create_app(issuer, store, verify_token)
    client = app.test_client()

    results = []
    passed = 0
    for name, token, method, path, expected, note in build_cases(issuer):
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.open(path, method=method, headers=headers)
        ok = resp.status_code == expected
        passed += ok
        results.append({
            "case": name, "endpoint": f"{method} {path}",
            "expected": expected, "got": resp.status_code, "ok": ok, "note": note,
        })

    # Sanity: a verifier that just rejects everything must FAIL the positive cases.
    positive_ok = all(
        r["ok"] for r in results
        if r["case"] in ("genuine_student_whoami", "genuine_admin_ok")
    )
    total = len(results)
    return {
        "verifier_passed": passed == total and positive_ok,
        "passed": passed,
        "total": total,
        "accepts_legitimate_tokens": positive_ok,
        "results": results,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lab 5 JWT integration grader")
    ap.add_argument("--verifier", required=True,
                    help="dotted module (ta.verifier_solution) or path to .py")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    verify_token = _load_verifier(args.verifier)
    report = run_matrix(verify_token)

    if args.json:
        import json
        print(json.dumps(report, indent=2))
        return 0 if report["verifier_passed"] else 1

    verdict = "PASS" if report["verifier_passed"] else "FAIL"
    print(f"Lab 5 JWT grader ({args.verifier}) — {verdict}  "
          f"{report['passed']}/{report['total']}")
    for r in report["results"]:
        mark = "OK " if r["ok"] else "XX "
        print(f"  [{mark}] {r['case']:<28} {r['endpoint']:<20} "
              f"expect {r['expected']} got {r['got']}  — {r['note']}")
    if not report["accepts_legitimate_tokens"]:
        print("  !! verifier rejects legitimate tokens (a reject-all verifier fails here)")
    return 0 if report["verifier_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
