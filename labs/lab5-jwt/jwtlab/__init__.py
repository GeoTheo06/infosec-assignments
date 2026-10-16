"""jwtlab — shared library for Lab 5 (JWT privilege escalation & verifier repair).

Modules:
    keys        RSA keypair generation and PEM (de)serialization.
    issuer      Token issuance (holds the private signing key).
    authz       Account store + authorization (401 vs 403 semantics).
    vulnerable  The intentionally broken verifier shipped in the lab server.
    app         Flask app factory; the verifier callable is injected.

The student-editable repair lives OUTSIDE this package (student/verifier_repair.py);
the TA reference lives in ta/verifier_solution.py. Both are graded by importing
them and injecting into the same app/authz code here, so validation and
permission logic are assessed separately.
"""
