#!/usr/bin/env python3
"""Grader for Lab 3 (DH MITM).

Runs a submitted `run_attack(api)` against FRESH in-process sessions, then
inspects Bob's actually-decrypted plaintext in private grader state (the
SessionManager), comparing it to the expected altered message — target fields
changed, session_id + the unknown memo preserved. A printed claim or a
student-returned plaintext is never trusted; only what Bob received counts.

Usage (from labs/lab3-dh-mitm):
    python -m grader.grade --attack ta.reference_attack
    python -m grader.grade --attack student.attack_stub --rounds 5
    python -m grader.grade --attack path/to/attack.py
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_ROOT))

from dhlab.peers import SessionManager      # noqa: E402
from dhlab.service import create_app        # noqa: E402


class TestClientApi:
    """`api` adapter backed by a Flask test client (same contract as LabClient)."""

    __test__ = False  # not a pytest test class

    def __init__(self, client):
        self.c = client

    def _json(self, resp):
        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.get_json()}")
        return resp.get_json()

    def params(self):
        return self._json(self.c.get("/params"))

    def create_session(self):
        return self._json(self.c.post("/sessions"))

    def substitute(self, sid, to_alice, to_bob):
        return self._json(self.c.post(
            f"/sessions/{sid}/substitute",
            json={"to_alice": str(to_alice), "to_bob": str(to_bob)}))

    def deliver(self, sid, packet):
        return self._json(self.c.post(f"/sessions/{sid}/deliver", json=packet))

    def transcript(self, sid):
        return self._json(self.c.get(f"/sessions/{sid}/transcript"))


def _load_attack(spec: str):
    if spec.endswith(".py"):
        path = Path(spec).resolve()
        ms = importlib.util.spec_from_file_location("submitted_attack", path)
        mod = importlib.util.module_from_spec(ms)
        ms.loader.exec_module(mod)  # type: ignore[union-attr]
    else:
        mod = importlib.import_module(spec)
    return getattr(mod, "run_attack")


def grade_once(run_attack) -> dict:
    manager = SessionManager()
    app = create_app(manager)
    api = TestClientApi(app.test_client())

    result = run_attack(api)
    sid = (result or {}).get("session_id")
    if not sid:
        return {"ok": False, "reason": "attack did not return a session_id"}

    session = manager._sessions.get(sid)
    if session is None:
        return {"ok": False, "reason": "unknown session id returned"}
    if session.bob_received is None:
        return {"ok": False, "reason": "Bob never received/decrypted a message"}

    expected = manager.expected_final_message(sid)
    got = session.bob_received
    ok = got == expected
    checks = {
        "recipient_changed": got.get("recipient") == "lab-account-B",
        "amount_changed": got.get("amount") == 900,
        "session_id_preserved": got.get("session_id") == expected["session_id"],
        "memo_preserved": got.get("memo") == expected["memo"],
        "receipt_recorded": result.get("receipt_id") in session.receipts,
    }
    return {
        "ok": ok and all(checks.values()),
        "session_id": sid,
        "bob_received_matches_expected": ok,
        "checks": checks,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lab 3 DH MITM grader")
    ap.add_argument("--attack", required=True,
                    help="dotted module (ta.reference_attack) or path to .py")
    ap.add_argument("--rounds", type=int, default=3,
                    help="number of fresh sessions to attack (all must pass)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    run_attack = _load_attack(args.attack)
    rounds = []
    all_ok = True
    for i in range(args.rounds):
        try:
            r = grade_once(run_attack)
        except NotImplementedError as exc:
            r = {"ok": False, "reason": f"not implemented: {exc}"}
        except Exception as exc:  # a broken attack should fail, not crash the grader
            r = {"ok": False, "reason": f"attack raised {type(exc).__name__}: {exc}"}
        all_ok = all_ok and r["ok"]
        rounds.append(r)

    report = {"attack": args.attack, "rounds": args.rounds,
              "passed": all_ok, "results": rounds}

    if args.json:
        import json
        print(json.dumps(report, indent=2))
        return 0 if all_ok else 1

    print(f"Lab 3 DH MITM grader ({args.attack}) — "
          f"{'PASS' if all_ok else 'FAIL'} over {args.rounds} fresh session(s)")
    for i, r in enumerate(rounds):
        if r["ok"]:
            print(f"  round {i+1}: OK  (Bob received the altered message; memo preserved)")
        else:
            reason = r.get("reason") or f"checks={r.get('checks')}"
            print(f"  round {i+1}: XX  {reason}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
