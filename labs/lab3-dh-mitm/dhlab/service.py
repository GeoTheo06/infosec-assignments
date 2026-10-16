"""Flask interception API for the DH MITM lab.

Contract:
    GET  /params                         fixed group parameters
    POST /sessions                       create a run -> {session_id, A, B, required_change}
    POST /sessions/<id>/substitute       {to_alice, to_bob} -> Alice's encrypted packet
    POST /sessions/<id>/deliver          {session_id?, nonce, ciphertext} -> {receipt_id}
    GET  /sessions/<id>/transcript       public events (no secrets)
    GET  /healthz

Associated data is bound server-side to the real session id, never to free
request fields. Private exponents, Alice's plaintext and derived keys are never
returned.
"""
from __future__ import annotations

from flask import Flask, jsonify, request

from .params import params_public
from .peers import SessionError, SessionManager


def _parse_int(value, name):
    try:
        return int(str(value))
    except (TypeError, ValueError):
        raise SessionError(400, f"{name} must be an integer (decimal string)")


def create_app(manager: SessionManager | None = None) -> Flask:
    app = Flask(__name__)
    manager = manager or SessionManager()
    app.config["MANAGER"] = manager

    @app.errorhandler(SessionError)
    def _handle(err: SessionError):
        return jsonify({"error": err.reason}), err.status

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    @app.get("/params")
    def params():
        return jsonify(params_public())

    @app.post("/sessions")
    def create_session():
        s = manager.create()
        out = {"params": params_public()}
        out.update(s.public_view())
        return jsonify(out), 201

    @app.post("/sessions/<sid>/substitute")
    def substitute(sid):
        body = request.get_json(silent=True) or {}
        to_alice = _parse_int(body.get("to_alice"), "to_alice")
        to_bob = _parse_int(body.get("to_bob"), "to_bob")
        packet = manager.substitute(sid, to_alice, to_bob)
        return jsonify({"alice_packet": packet})

    @app.post("/sessions/<sid>/deliver")
    def deliver(sid):
        body = request.get_json(silent=True) or {}
        packet = {
            "session_id": body.get("session_id", sid),
            "nonce": body.get("nonce"),
            "ciphertext": body.get("ciphertext"),
        }
        if not packet["nonce"] or not packet["ciphertext"]:
            raise SessionError(400, "nonce and ciphertext are required")
        return jsonify(manager.deliver(sid, packet))

    @app.get("/sessions/<sid>/transcript")
    def transcript(sid):
        s = manager.get(sid)
        return jsonify({"session_id": sid, "transcript": s.transcript})

    return app
