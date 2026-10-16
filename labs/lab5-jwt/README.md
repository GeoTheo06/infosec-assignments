# Lab 5 — JWT privilege escalation and verifier repair

A small Flask app issues RS256 JWTs. The shipped verifier decodes claims with
signature validation **disabled** (application misuse of PyJWT, not a vulnerable
library version). Students escalate to an admin endpoint, then repair one
`verify_token` function.

## Layout

```
lab5-jwt/
├─ jwtlab/              shared library (NOT student-editable)
│  ├─ keys.py           RSA keypair gen / PEM
│  ├─ issuer.py         RS256 token issuance (holds private key)
│  ├─ authz.py          account store + 401/403 authorization
│  ├─ vulnerable.py     the broken verifier (unverified decode)
│  └─ app.py            Flask factory; verifier is injected
├─ app/server.py        runnable server (broken by default; env to swap verifier)
├─ student/
│  ├─ verifier_repair.py   ← students implement verify_token here
│  ├─ token_editor.py      decode / tamper / alg:none helper + CLI
│  └─ HANDOUT.md
├─ ta/verifier_solution.py  ← TA reference (do not ship)
├─ grader/grade.py          ← integration grader (fresh keys/accounts; 17-case matrix)
├─ tests/test_jwt.py        ← pytest
├─ conftest.py
└─ README.md
```

## Run it

```bash
pip install -r ../../workspace/requirements.txt   # cryptography, PyJWT, Flask

python app/server.py                               # broken — attack works
JWTLAB_VERIFIER=ta.verifier_solution python app/server.py   # repaired — blocked
```

Endpoints: `POST /login`, `POST /reissue`, `GET /whoami`, `GET /admin/marker`,
`GET /pubkey`, `GET /healthz`. Config via `JWTLAB_*` env vars (see `app/server.py`).

## Grade a verifier

```bash
python -m grader.grade --verifier ta.verifier_solution     # -> PASS 17/17
python -m grader.grade --verifier student.verifier_repair  # -> FAIL until implemented
python -m grader.grade --verifier path/to/their_verifier.py
```

The grader builds a **fresh** issuer (fresh RSA keys), fresh accounts and
freshly minted adversarial tokens each run, so a submission can't hard-code
values. It recomputes every status itself and distinguishes 401 from 403.

## Tests

```bash
pytest tests -q      # 8 tests
```

They assert: the broken server **is** exploitable (role forge + identity swap
reach the admin marker), the TA verifier passes the full matrix and keeps
genuine tokens working, the un-implemented stub fails because it rejects
legitimate tokens, login never honors a client-chosen role, and cross-group
accounts are isolated.

## Design notes mapped to the brief

| Brief point | Implementation |
|---|---|
| RS256; private key in backend; students get public key + user token | `issuer.py` holds the private PEM; `GET /pubkey` serves the public key; `/login` issues the account's role. |
| Protected endpoint trusts the **verified** role and requires a group account | `authz.authorize_admin` — the verifier is the security boundary; authz only adds group membership + role. |
| Login must not accept a client-selected admin role | `/login` ignores any body `role`; issues `acct.role`. |
| Broken verifier = PyJWT unverified decode, not an old-package CVE | `jwtlab/vulnerable.py`. |
| Repaired verifier pins algorithm, checks iss/aud/exp/required claims | `ta/verifier_solution.py`; algorithm pinned to `["RS256"]`. |
| Student repair separate from grader secrets/authz | repair is injected; authz + issuer keys live outside the editable file. |
| Integration grader exercises verifier + endpoint; 401 vs 403 | `grader/grade.py`. |
| Fresh keys/accounts/claims in hidden tests | grader mints everything fresh per run. |
| Reset/reissue without exposing signing key | `POST /reissue` returns a fresh token; the key never leaves the issuer. |

## Reset procedure

Per-instance state is in-process. To reset: restart `app/server.py` (fresh RSA
keypair + fresh tokens), or call `POST /reissue` with a current token for a new
one. No signing key is ever written to disk or returned to the client. For a new
group/run, set `JWTLAB_GROUP` / `JWTLAB_RUN`.

## Shipping to students

Ship `student/`, `app/`, `jwtlab/` and `conftest.py`. **Do not ship** `ta/`.
The `grader/` can ship (it imports the student module by name) but the TA runs
it server-side with hidden fresh fixtures for the real grade.
