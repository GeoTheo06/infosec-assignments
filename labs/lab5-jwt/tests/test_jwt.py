"""Lab 5 acceptance tests.

Covers: the broken verifier IS exploitable (so the attack lesson is real), the
TA repaired verifier passes the full matrix, the un-implemented student stub
fails (because it rejects legitimate tokens), and login never issues a
client-chosen admin role.
"""
import importlib

import jwt
import pytest

from grader.grade import run_matrix
from jwtlab.app import create_app
from jwtlab.authz import default_store
from jwtlab.issuer import Issuer
from jwtlab.vulnerable import verify_token as vulnerable_verify
from student.token_editor import tamper

ISS = "https://issuer.infosec-lab.example/"
AUD = "infosec-lab"


def _client(verify_token):
    issuer = Issuer(ISS, AUD, lifetime_seconds=3600)
    store = default_store()
    app = create_app(issuer, store, verify_token)
    return issuer, store, app.test_client()


# --- the attack works against the broken server -------------------------------

def test_vulnerable_server_is_exploitable():
    issuer, _store, client = _client(vulnerable_verify)
    student_tok = issuer.issue("alice", "student")
    # baseline: as a student, admin op is refused by authz
    r = client.get("/admin/marker", headers={"Authorization": f"Bearer {student_tok}"})
    assert r.status_code == 403
    # attack: tamper role -> admin, keep original signature
    forged = tamper(student_tok, {"role": "admin"})
    r = client.get("/admin/marker", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 200
    assert "ADMIN-OK" in r.get_json()["marker"]


def test_vulnerable_accepts_identity_swap():
    issuer, _store, client = _client(vulnerable_verify)
    student_tok = issuer.issue("alice", "student")
    forged = tamper(student_tok, {"sub": "root", "role": "admin"})
    r = client.get("/admin/marker", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 200


# --- the repaired (TA) verifier blocks the attack and passes the matrix --------

def test_ta_solution_passes_full_matrix():
    sol = importlib.import_module("ta.verifier_solution")
    report = run_matrix(sol.verify_token)
    failing = [r for r in report["results"] if not r["ok"]]
    assert report["verifier_passed"], f"failing cases: {failing}"
    assert report["passed"] == report["total"]


def test_repaired_blocks_tampering_but_keeps_genuine():
    from ta.verifier_solution import verify_token as secure
    issuer, _store, client = _client(secure)
    student_tok = issuer.issue("alice", "student")
    admin_tok = issuer.issue("root", "admin")
    # genuine student authenticates
    assert client.get("/whoami", headers={"Authorization": f"Bearer {student_tok}"}).status_code == 200
    # genuine admin succeeds
    assert client.get("/admin/marker", headers={"Authorization": f"Bearer {admin_tok}"}).status_code == 200
    # tampered token rejected (401, not 403)
    forged = tamper(student_tok, {"role": "admin"})
    assert client.get("/admin/marker", headers={"Authorization": f"Bearer {forged}"}).status_code == 401


# --- the un-implemented student stub must fail -------------------------------

def test_student_stub_fails_because_it_rejects_everything():
    stub = importlib.import_module("student.verifier_repair")
    report = run_matrix(stub.verify_token)
    assert not report["verifier_passed"]
    assert not report["accepts_legitimate_tokens"]


# --- login must not honor a client-chosen role -------------------------------

def test_login_issues_real_role_only():
    issuer, _store, client = _client(vulnerable_verify)
    # client tries to request admin at login; server ignores it
    r = client.post("/login", json={"username": "alice", "password": "student-pw-alice",
                                     "role": "admin"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["role_issued"] == "student"
    claims = jwt.decode(body["token"], options={"verify_signature": False})
    assert claims["role"] == "student"


def test_login_rejects_bad_credentials():
    issuer, _store, client = _client(vulnerable_verify)
    r = client.post("/login", json={"username": "alice", "password": "wrong"})
    assert r.status_code == 401


def test_cross_group_account_is_isolated():
    # otheradmin exists only in group-99; a token for it should get 403 here.
    from ta.verifier_solution import verify_token as secure
    issuer, _store, client = _client(secure)
    tok = issuer.issue("otheradmin", "admin")  # validly signed for this issuer
    r = client.get("/admin/marker", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 403
