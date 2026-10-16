# Lab 5 — Become admin in sixty seconds (then fix it)

You log in as an ordinary student. Within a minute you'll be an administrator —
without knowing any password, without touching the database, and the server
will hand you the keys itself. Then comes the better half: you'll find the one
missing line that made it possible and close the hole *without* locking out the
real admins.

Remember the JWT slide from Access Control — header, payload, signature, and
`RS256(base64url(header) + "." + base64url(payload), private_key)`? We're about
to find out what happens when a server reads the header and payload but forgets
to check that signature. (Spoiler from the design-principles slide: this is
**Complete Mediation** — "every access should be checked" — failing in the most
literal way possible.)

## Where this sits in the course

This lab is the Access Control lecture with your hands on it:

- **AuthN vs AuthZ.** The lecture's first distinction. Watch for it in the
  status codes: **401** = "I don't believe you're who you say" (authentication
  failed); **403** = "I believe you, but you're not allowed" (authorization
  failed). Keeping those straight *is* half the assignment.
- **The token.** Same `iss / aud / sub / role / exp` claims, same
  `role: student` the slide showed. RS256 is RSA signing from Crypto 2 — the
  issuer signs with its private key, you only get the public key.
- **Complete Mediation & Open Design.** The bug is a mediation failure. The fix
  is not hiding anything (Open Design: "secrecy should not be the source of
  security") — the attacker can read the whole token; security comes from the
  *signature check*, not from the token being secret.
- **Think like an attacker** (GPG lecture): what does the attacker control here?
  The whole token. So anything the server trusts *without verifying* is yours to
  forge.

## Setup

From the lab root (`labs/lab5-jwt`), with the course Python environment active:

```bash
python app/server.py          # the broken server, on http://127.0.0.1:5005
```

Demo accounts (synthetic): `alice` / `student-pw-alice` (a student), and there's
an admin account you are *not* given the password for — you won't need it.

Useful endpoints: `POST /login`, `GET /whoami`, `GET /admin/marker`
(admin-only), `GET /pubkey`.

## Part A — the attack

1. Log in as `alice`, keep the token.
2. Look inside it. A JWT is just base64url — no decryption needed:
   ```bash
   python -m student.token_editor decode <token>
   ```
   (You can also paste it into <https://jwt.io>, exactly as the lecture slide
   suggested — same thing, prettier.)
3. Confirm the baseline: as a student, `GET /admin/marker` says **403**. You're
   authenticated, just not allowed. (That's the AuthN/AuthZ line in action.)
4. Now forge. Change a claim but keep the original signature bytes:
   ```bash
   python -m student.token_editor tamper <token> --set role=admin
   ```
   Send that as `Authorization: Bearer <forged>` to `GET /admin/marker`. It
   works — because the server never checked whether the signature still matches
   the payload. Try `--set sub=root --set role=admin` too (identity swap).

Write down the marker you got and, in one sentence, **which check was missing.**

## Part B — the repair

Implement `verify_token` in [`verifier_repair.py`](verifier_repair.py). You're
not rebuilding JWTs or RSA — you're adding the validation the lecture says must
be there. It must:

- **verify the RS256 signature** with the public key;
- **pin the algorithm to RS256** yourself — never trust the token header's `alg`
  to choose it (this is what blocks the `alg:none` and HS256-confusion tricks;
  PyJWT literally warns about this);
- enforce `iss == expected_issuer` and `aud == expected_audience`;
- require `iss, aud, sub, role, exp`, and reject expired tokens;
- reject a bad `role` or non-string `sub` cleanly (no crash);
- return the validated claims, or raise `jwt.InvalidTokenError`.

Note the division of labour, straight from the lecture: **your function does
authentication** (is this token real and valid?). The **authorization** —
role → permission, right group — lives in `jwtlab/authz.py` and is graded
separately. Don't reimplement it; a correct verifier plus the existing authz is
what turns the 401s and 403s on correctly.

Grade it (fresh keys and accounts every run, so nothing can be hard-coded):

```bash
python -m grader.grade --verifier student.verifier_repair
```

Re-run the Part A attack against your fixed server to watch it bounce:

```bash
JWTLAB_VERIFIER=student.verifier_repair python app/server.py
```

## What "done" looks like

| Case | After your repair |
|------|-------------------|
| Genuine student token | authenticates; admin op **403** |
| Genuine admin token | admin op **200** |
| Edited role/subject (old signature) | **401** |
| Corrupted signature / wrong key | **401** |
| `alg:none` / unapproved algorithm | **401** |
| Expired token | **401** |
| Missing claim / wrong issuer or audience | **401** |
| Valid token, account from another group | **403** |

The sly trap: a verifier that just rejects *everything* passes most of these —
and fails the two genuine-token rows. Good security isn't "say no a lot"; it's
"say yes to exactly the right things." That's the whole lecture in one sentence.

## Hand in

- Your `verifier_repair.py`.
- A short note: the token you forged, the marker you got, the missing check, and
  why pinning the algorithm matters (what could the attacker do if you let the
  header choose it?).
- Grader output showing your verifier passing.
