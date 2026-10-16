# Lab 3 — Unauthenticated DH MITM with message alteration

Active man-in-the-middle on an **unauthenticated** Diffie–Hellman exchange. The
attacker uses two of their own exponents (not the parameter-injection shortcut),
holds a different key with each peer, and must read → alter → re-encrypt →
deliver Alice's message so Bob accepts it.

## Layout

```
lab3-dh-mitm/
├─ dhlab/                 shared library (NOT student-editable)
│  ├─ params.py           RFC 3526 group 14 (g=2, q=(p-1)/2) + subgroup check
│  ├─ crypto.py           fixed serialization, HKDF-SHA256, AES-GCM helpers
│  ├─ peers.py            Alice/Bob state, leg establishment, Bob's decrypt/validate
│  └─ service.py          Flask interception API
├─ service/server.py      runnable service (port 5006)
├─ student/
│  ├─ client.py           LabClient (HTTP) + re-exported helpers
│  ├─ attack_stub.py      ← students implement run_attack(api)
│  └─ HANDOUT.md
├─ ta/reference_attack.py  ← TA reference MITM (do not ship)
├─ grader/grade.py         ← fresh-session grader w/ private plaintext inspection
├─ tests/test_dh.py        ← pytest
├─ conftest.py
└─ README.md
```

## Run

```bash
pip install -r ../../workspace/requirements.txt
python service/server.py          # http://127.0.0.1:5006
```

API: `GET /params`, `POST /sessions`, `POST /sessions/<id>/substitute`,
`POST /sessions/<id>/deliver`, `GET /sessions/<id>/transcript`, `GET /healthz`.

## Grade / test

```bash
python -m grader.grade --attack ta.reference_attack --rounds 3   # PASS
python -m grader.grade --attack student.attack_stub              # FAIL until implemented
pytest tests -q                                                  # 8 tests
```

The grader runs the submitted `run_attack` against fresh in-process sessions and
then reads Bob's actually-decrypted plaintext from private `SessionManager`
state, comparing it to the expected altered message (target fields changed,
`session_id` + the unknown `memo` preserved). It never trusts a returned/printed
plaintext.

## Design notes mapped to the brief

| Brief point | Implementation |
|---|---|
| Two attacker exponents, valid public values (not param-injection) | `ta/reference_attack.py` picks fresh `x,y`, sends `g^x,g^y`. |
| RFC 3526 group 14, g=2, q=(p-1)/2, exponents from subgroup via `secrets` | `dhlab/params.py`, `peers.create()`. |
| Validate incoming public values (exclude trivial; require subgroup) | `params.is_valid_public` (`1<v<p-1` and `v^q==1`). |
| HKDF-SHA256 from fixed-width secret; documented salt/info | `crypto.derive_key` (256-byte BE; salt=SHA256(sid); info=`infosec-dh-lab-v1`). |
| AES-GCM, 12-byte nonce, session id as AAD, included in message | `crypto.encrypt/decrypt`; AAD bound server-side. |
| API: create / substitute / deliver | `dhlab/service.py`. |
| AAD derived from documented session id, not trusted request data | `crypto._aad(session_id)`; deliver uses the server's session id. |
| Fresh unknown memo so fabrication fails | `peers.create()` random `memo-<hex>`. |
| Grader inspects Bob's received plaintext in private state | `grader.grade_once` reads `manager._sessions[sid].bob_received`. |
| Transcript shows public events; hides private exponents/keys/plaintext | `GET /transcript` returns only public events. |

## Reset procedure

Sessions live in-process. Restart `service/server.py` to clear all runs, or just
`POST /sessions` for a brand-new run (fresh exponents, fresh memo). No persisted
state; nothing to scrub between students other than restarting the process (or
running one isolated instance per group).

## Shipping to students

Ship `dhlab/`, `service/`, `student/`, `conftest.py`. **Do not ship** `ta/`. The
grader may ship (imports the student's module) but the real grade runs
server-side over fresh sessions.
