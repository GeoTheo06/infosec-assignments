# Lab 3 — Sit in the middle of Diffie–Hellman

Alice is about to send Bob $10. Bob is about to receive a request for **$900**,
to a different account — and both of them will finish the exchange convinced the
maths checked out and nobody was listening. You're the reason. The catch that
keeps you honest: Alice's message contains a random note you can't guess, so you
can't fake the message — you have to genuinely read hers, change two fields, and
re-seal it.

You do **not** crack Diffie–Hellman. You don't recover anyone's private
exponent, you don't break AES. The discrete-log problem stays unbroken the whole
time. This attack works for one reason only, and it's the reason the Protocols
lecture kept hammering: **the key exchange is unauthenticated.** Nobody checks
*who* sent the public value.

## Where this sits in the course

This is the Crypto 2 DH slide and the Protocols MiM slides, live:

- **Diffie–Hellman** (Crypto 2): public `p`, `g`; Alice picks secret `a` and
  sends `A = gᵃ mod p`; Bob picks `b` and sends `B = gᵇ mod p`; both get
  `S = gᵃᵇ`. The slide asked *"what does the attacker know?"* — answer: `p, g,
  A, B`, never `a` or `b`. You're about to use exactly that knowledge.
- **The exact attack** (Protocols, Perfect Forward Secrecy slide): the lecture
  literally says unauthenticated ephemeral DH is open to MiM, and *"to prevent
  the MiM attack, the initial communication must be encrypted using the long
  term key."* You're going to *be* that MiM, and then explain that one-line fix.
- **"What if Eve takes Alice's place?"** (Protocols): that's your job description
  this week. You'll hold one shared key with Alice and a *different* one with
  Bob, and relay between them.
- **Signing to fix it** (GPG / PKI authentication): the repair is the fake-key /
  key-substitution defence from the GPG lecture — if each peer *signed* its
  public value with a key the other already trusts, your substitution falls
  apart.

A couple of pieces are slightly beyond the slides — here's the bridge:

- You derive a 32-byte key from the shared secret `S` with **HKDF** (the Crypto 2
  slide even says the shared secret "can then be used to derive a symmetric
  key"). HKDF is just a hash-based key derivation — the SHA-256 you know, used to
  turn `S` into a clean key.
- Messages use **AES-GCM**. Think of it as **CTR mode** (Crypto 1) for
  confidentiality *plus* a built-in **MAC/tag** (Hashing lecture) for integrity —
  "authenticated encryption". The helper handles the nonce and tag; you just call
  `encrypt` / `decrypt`.

## Setup

```bash
python service/server.py            # the Alice/Bob service, on http://127.0.0.1:5006
```

```python
from student.client import LabClient
api = LabClient("http://127.0.0.1:5006")
s = api.create_session()
print(s["A"], s["B"], s["required_change"])
```

**Fixed protocol** (don't reinvent it — it's the same everyone uses so the attack
is about *authentication*, not weak parameters): RFC 3526 group 14, `g = 2`,
`q = (p-1)/2` — a safe prime, exactly the "p = 2q+1" recommendation from the DH
slide. The service validates the public values you send (no `0`, `1`, `p-1`; must
be in the order-`q` subgroup), so you must send genuine `gˣ`, `gʸ`.

Helpers you get (so you implement none of the maths from scratch):
`P, G, Q, is_valid_public, modexp, derive_key, encrypt, decrypt`.

## Your task — `student/attack_stub.py :: run_attack(api)`

You're Trudy, between Alice and Bob:

1. `api.create_session()` → read `A`, `B`, `p`, `g`.
2. Pick your **own** secret exponents `x`, `y` (use `secrets`). Send `gˣ` to
   Alice and `gʸ` to Bob via `api.substitute(sid, to_alice, to_bob)`. That call
   hands you back Alice's encrypted packet — because Alice, thinking `gˣ` came
   from Bob, encrypted under the key *she* derived.
3. Your shared secret with Alice is `Aˣ mod p`; with Bob it's `Bʸ mod p`. (Check
   you see why those match what Alice and Bob each computed — this is the whole
   trick.) Derive both keys with `derive_key`.
4. `decrypt` Alice's packet. Change `recipient` → `"lab-account-B"` and `amount`
   → `900`. **Keep `session_id` and `memo` exactly** — the memo is random and you
   only know it because you decrypted. Re-`encrypt` under your Bob-side key.
5. `api.deliver(sid, packet)` and return `{"session_id": ..., "receipt_id": ...}`.

Grade it (fresh sessions each run — a correct attack survives new random values):

```bash
python -m grader.grade --attack student.attack_stub --rounds 5
```

## Why authenticated encryption didn't save them

Here's the part worth sitting with: AES-GCM is *authenticated* encryption, and
you still waltzed through. Why? Because you weren't tampering with ciphertext —
you held a **legitimate key on each side** and produced a perfectly valid tag for
Bob. GCM guarantees "this came from someone who knew the key"; it never promised
that someone was Alice. Integrity ≠ authentication of the *peer*. The missing
control is authenticating the DH exchange itself.

Short written answer to hand in: using the GPG lecture's signing, explain how
having each peer **sign its public value** with a key the other already trusts
would stop you cold. (Which of your two substitutions breaks first, and why?)
Implementing the fix is optional this week — explaining it is not.

## Acceptance checks

- A normal relay (forward the real values) delivers Alice's original message.
- A ciphertext-only byte-flip fails GCM at Bob (try it — feel the tag bite).
- The full MiM makes Bob receive the changed fields **and the original
  memo/session_id**. The grader reads what Bob actually decrypted, not what you
  claim — so you really do have to recover that memo.
- Fresh random sessions don't break a correct attack.

Cryptopals Challenge 34 is a close cousin if you want extra reading — but note
its headline trick (parameter injection) is *not* this task; we use two honest
attacker exponents, which is the version that still works against careful
parameter checks.
