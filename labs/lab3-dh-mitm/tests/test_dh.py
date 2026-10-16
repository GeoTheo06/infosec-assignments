"""Lab 3 acceptance tests.

Covers: a normal relay delivers the original message; a ciphertext-only byte
edit fails GCM; the full two-exponent MITM succeeds and Bob receives the target
fields AND the original memo/session_id; fresh sessions don't break a correct
attack; invalid public values are rejected; the student stub fails.
"""
import base64
import json

import pytest

from dhlab.peers import SessionManager
from dhlab.service import create_app
from grader.grade import TestClientApi, grade_once


def _fresh():
    manager = SessionManager()
    app = create_app(manager)
    return manager, app.test_client()


def test_params_and_session_shape():
    _m, c = _fresh()
    r = c.post("/sessions")
    assert r.status_code == 201
    body = r.get_json()
    assert set(["session_id", "A", "B", "required_change", "params"]) <= set(body)
    assert body["params"]["g"] == 2


def test_normal_relay_delivers_original():
    manager, c = _fresh()
    body = c.post("/sessions").get_json()
    sid, A, B = body["session_id"], int(body["A"]), int(body["B"])
    # Honest relay: give Alice the real B and Bob the real A -> same key g^(ab).
    packet = c.post(f"/sessions/{sid}/substitute",
                    json={"to_alice": str(B), "to_bob": str(A)}).get_json()["alice_packet"]
    r = c.post(f"/sessions/{sid}/deliver", json=packet)
    assert r.status_code == 200
    session = manager._sessions[sid]
    assert session.bob_received == session.alice_plaintext
    assert session.bob_received["recipient"] == "lab-account-A"
    assert session.bob_received["amount"] == 10


def test_ciphertext_byte_edit_fails_gcm():
    manager, c = _fresh()
    body = c.post("/sessions").get_json()
    sid, A, B = body["session_id"], int(body["A"]), int(body["B"])
    packet = c.post(f"/sessions/{sid}/substitute",
                    json={"to_alice": str(B), "to_bob": str(A)}).get_json()["alice_packet"]
    # Flip one byte of the ciphertext; the GCM tag must reject it.
    raw = bytearray(base64.b64decode(packet["ciphertext"]))
    raw[0] ^= 0x01
    packet["ciphertext"] = base64.b64encode(bytes(raw)).decode()
    r = c.post(f"/sessions/{sid}/deliver", json=packet)
    assert r.status_code == 422
    assert "InvalidTag" in r.get_json()["error"]


def test_invalid_public_values_rejected():
    manager, c = _fresh()
    body = c.post("/sessions").get_json()
    sid = body["session_id"]
    p = int(body["params"]["p"])
    for bad in ("1", str(p - 1), "0"):
        r = c.post(f"/sessions/{sid}/substitute",
                   json={"to_alice": bad, "to_bob": bad})
        assert r.status_code == 400


def test_full_mitm_reference_attack_succeeds():
    import ta.reference_attack as ref
    report = grade_once(ref.run_attack)
    assert report["ok"], report
    assert report["bob_received_matches_expected"]
    assert all(report["checks"].values())


def test_fresh_sessions_do_not_break_correct_attack():
    import ta.reference_attack as ref
    for _ in range(5):
        report = grade_once(ref.run_attack)
        assert report["ok"], report


def test_mitm_preserves_unknown_memo_and_session_id():
    import ta.reference_attack as ref
    manager = SessionManager()
    app = create_app(manager)
    api = TestClientApi(app.test_client())
    result = ref.run_attack(api)
    sid = result["session_id"]
    session = manager._sessions[sid]
    original_memo = session.alice_plaintext["memo"]
    assert session.bob_received["memo"] == original_memo
    assert session.bob_received["session_id"] == sid
    assert session.bob_received["recipient"] == "lab-account-B"
    assert session.bob_received["amount"] == 900


def test_student_stub_fails():
    import student.attack_stub as stub
    report = grade_once(stub.run_attack) if False else None
    # grade_once would raise NotImplementedError; the grader CLI catches it, but
    # here we assert the stub is not a working attack.
    with pytest.raises(NotImplementedError):
        stub.run_attack(object())
