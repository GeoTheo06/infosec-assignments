"""Flask app factory for the JWT lab.

The verifier is INJECTED: the same app serves either the broken verifier
(`jwtlab.vulnerable`) or a repaired one (student / TA). Authorization lives in
`authz` and is not part of the injected code.

Endpoints:
    POST /login            {username, password}        -> {token}  (real role only)
    POST /reissue          Authorization: Bearer <tok> -> {token}  (fresh token, same sub)
    GET  /whoami           Authorization: Bearer <tok> -> {sub, role, group}
    GET  /admin/marker     Authorization: Bearer <tok> -> {marker} (admin-only, group-scoped)
    GET  /pubkey           -> PEM public verification key
    GET  /healthz          -> ok
"""
from __future__ import annotations

from typing import Callable

import jwt
from flask import Flask, g, jsonify, request

from .authz import AccountStore, AuthzError, authorize_admin, whoami
from .issuer import Issuer

Verifier = Callable[[str, bytes, str, str], dict]


def create_app(issuer: Issuer, store: AccountStore, verify_token: Verifier) -> Flask:
    app = Flask(__name__)

    def _bearer() -> str | None:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[len("Bearer "):].strip()
        return None

    def _authenticate() -> dict:
        """Run the injected verifier; translate failure to 401."""
        token = _bearer()
        if not token:
            raise AuthzError(401, "missing bearer token")
        try:
            claims = verify_token(
                token, issuer.public_pem, issuer.issuer, issuer.audience
            )
        except jwt.InvalidTokenError as exc:
            raise AuthzError(401, f"invalid token: {exc}") from exc
        except Exception as exc:  # a verifier that raises anything else = reject
            raise AuthzError(401, f"invalid token: {exc}") from exc
        if not isinstance(claims, dict):
            raise AuthzError(401, "verifier did not return claims")
        return claims

    @app.errorhandler(AuthzError)
    def _handle_authz(err: AuthzError):
        return jsonify({"error": err.reason}), err.status

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    @app.get("/pubkey")
    def pubkey():
        return app.response_class(issuer.public_pem, mimetype="application/x-pem-file")

    @app.post("/login")
    def login():
        body = request.get_json(silent=True) or {}
        username = body.get("username", "")
        password = body.get("password", "")
        acct = store.by_login(username, password)
        if acct is None:
            return jsonify({"error": "bad credentials"}), 401
        # IMPORTANT: issue the account's REAL role, never a client-supplied one.
        token = issuer.issue(acct.sub, acct.role)
        return jsonify({"token": token, "role_issued": acct.role})

    @app.post("/reissue")
    def reissue():
        claims = _authenticate()
        sub = claims.get("sub")
        acct = store.in_current_group(sub) if isinstance(sub, str) else None
        if acct is None:
            raise AuthzError(403, "account not in this group")
        return jsonify({"token": issuer.issue(acct.sub, acct.role)})

    @app.get("/whoami")
    def whoami_route():
        claims = _authenticate()
        g.claims = claims
        return jsonify(whoami(claims, store))

    @app.get("/admin/marker")
    def admin_marker():
        claims = _authenticate()        # 401 on bad token
        marker = authorize_admin(claims, store)   # 403 on insufficient perms
        return jsonify({"marker": marker})

    return app
