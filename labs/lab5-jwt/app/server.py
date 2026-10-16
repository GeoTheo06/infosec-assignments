#!/usr/bin/env python3
"""Runnable JWT lab server.

By default it wires the BROKEN verifier (jwtlab.vulnerable) so students can
perform the privilege-escalation attack. Point JWTLAB_VERIFIER at a module that
exposes `verify_token(token, public_key, expected_issuer, expected_audience)`
to run with a repaired verifier (e.g. the TA solution or a student's).

    # broken (default) — attack works
    python app/server.py

    # repaired — attack is blocked
    JWTLAB_VERIFIER=ta.verifier_solution python app/server.py

Env:
    JWTLAB_GROUP     (default group-01)
    JWTLAB_RUN       (default run-0001)
    JWTLAB_ISS       (default https://issuer.infosec-lab.example/)
    JWTLAB_AUD       (default infosec-lab)
    JWTLAB_PORT      (default 5005)
    JWTLAB_LIFETIME  (seconds, default 3600)
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

# Make `jwtlab`, `ta`, `student` importable regardless of cwd.
LAB_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_ROOT))

from jwtlab.app import create_app          # noqa: E402
from jwtlab.authz import default_store      # noqa: E402
from jwtlab.issuer import Issuer            # noqa: E402


def load_verifier(dotted: str):
    mod = importlib.import_module(dotted)
    return getattr(mod, "verify_token")


def build():
    group = os.environ.get("JWTLAB_GROUP", "group-01")
    run = os.environ.get("JWTLAB_RUN", "run-0001")
    iss = os.environ.get("JWTLAB_ISS", "https://issuer.infosec-lab.example/")
    aud = os.environ.get("JWTLAB_AUD", "infosec-lab")
    lifetime = int(os.environ.get("JWTLAB_LIFETIME", "3600"))
    verifier_mod = os.environ.get("JWTLAB_VERIFIER", "jwtlab.vulnerable")

    issuer = Issuer(iss, aud, lifetime_seconds=lifetime)
    store = default_store(group=group, run_id=run)
    verify_token = load_verifier(verifier_mod)
    app = create_app(issuer, store, verify_token)
    app.config["ISSUER"] = issuer
    app.config["STORE"] = store
    print(f"[jwtlab] verifier={verifier_mod} group={group} run={run}", file=sys.stderr)
    print(f"[jwtlab] demo logins: alice/student-pw-alice (student), "
          f"root/admin-pw-root (admin)", file=sys.stderr)
    return app


if __name__ == "__main__":
    build().run(port=int(os.environ.get("JWTLAB_PORT", "5005")))
