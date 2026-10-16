# Lab 4 — Same people, two leaks, four ways to store a password

Two databases leak. Same twelve people, same passwords — but each database
stored them differently. Against the first, cracking everyone costs you 6,144
guesses. Then you try the others: one lets you **reuse almost all that work for
free**, one makes you throw it away and start over, and one is built to make you
pay the full price *per account, forever*. Your job is to predict which is which
— and then prove it with a guess counter you can't lie to.

The Protocols lecture had a one-liner that this whole lab unpacks: *"search the
hash in Rainbow Tables — not feasible with salted password hashes."* By the end
you'll know **exactly** why "salted" changes everything, and it's not the reason
most people think (a salt is *public*; it doesn't make any single password
harder to guess).

## Where this sits in the course

- **The password problem** (Protocols): guessable, reused, weak by nature — and
  the **"numbers game"** (is 2⁶³ enough?). This lab is offline guessing, the
  scary side of that slide.
- **Hashing** (Hashing lecture): SHA-256 is your fast hash; the expensive scheme
  uses **PBKDF2 = HMAC-SHA256 repeated**, i.e. the HMAC you already built, run
  thousands of times to make each guess cost more.
- **Rainbow tables** (Protocols + the bonus): the lecture's claim, made concrete.
  You'll build a lookup table *and* a real rainbow table and see why a salt
  wrecks both.
- **Think like an attacker** (GPG): the recurring question — *what work can I
  reuse?* Salts are an answer to that question, not to "how strong is this one
  password".

## The four schemes

| Scheme | How it stores a password |
|--------|--------------------------|
| A | `SHA256(password)` — no salt |
| B | `SHA256(password ‖ salt)` — **one shared** salt for everyone |
| C | `SHA256(password ‖ salt)` — a **different** salt per person |
| D | `PBKDF2-HMAC-SHA256(password, salt, iterations)` — per-person salt, deliberately slow |

Encoding is spelled out so nothing is ambiguous: passwords are ASCII; a salt is
a 32-character hex **string** and those characters are hashed as-is (not
hex-decoded). You never implement the hashing — you call `oracle.digest(pw,
salt)`, and the oracle *counts every call*. That counter is the real score;
timing is just an observation.

## Setup

```bash
# stdlib only for the core lab; you just need the course Python env for pytest
python -c "from passlab.generator import make_release; print(make_release(1,'C').public_json())"
```

## Your task — `student/strategy.py :: recover(...)`

```python
def recover(rows, candidates, oracle, full_pass=False) -> {account_id: password}
```

- `rows`: `{account_id, scheme, salt, digest[, iterations]}` — `salt` is `None`
  for A, shared for B, per-row for C/D.
- `candidates`: the fixed list of passwords to try.
- `oracle.digest(pw, salt)`: the counted hasher for this scheme.
- `full_pass`: `True` → try every candidate against every distinct salt (stable,
  comparable counts); `False` → you may stop a salt group once it's solved.

**The one insight that matters:** group the rows by salt and hash each candidate
**once per distinct salt**, not once per account. `from passlab.runner import
group_by_salt` does the grouping. A student who loops per-account does *way* more
work — and you should be able to say exactly how much more, and why.

Grade it (fresh, unseen databases; your counts are recomputed by the harness):

```bash
python -m grader.grade --strategy student.strategy --rounds 3
```

## The experiments to run and write up

1. **Count the guesses.** Full-pass A, B, C. You should get **A = 512, B = 512,
   C = 6,144.** Explain why A and B tie, and why C is exactly 12× B. (This is the
   payoff of the grouping insight.)
2. **Reuse across the two leaks** (`passlab.reuse.run_reuse_experiment`): take a
   table you built for leak #1 and point it at leak #2 with (a) the same shared
   salt, (b) a changed shared salt, (c) no salt, (d) fresh per-row salts. Record
   which let you reuse the work and which forced a recompute. *This* is the
   rainbow-tables slide: the salt doesn't protect a weak password from being
   guessed — it stops the attacker **amortising** one effort across accounts and
   releases.
3. **Cheap vs expensive** (scheme D, `passlab.benchmark`): same attack, tiny
   database (2 accounts, 128 candidates), a few iteration counts. Report the
   guess counts (authoritative) and the wall-clock (just an observation). Feel
   how PBKDF2's iterations turn "seconds" into "please don't".

## What you hand in

Recovered account→password mappings, your `recover` function, a table of guess
counts, your timing notes, and short answers on reuse. One sentence I want to see
somewhere: *why a public salt still forces per-account work even though it makes
no single password harder to guess.*

## Acceptance checks

In-list passwords are recovered; out-of-list ones stay unrecovered (a bounded
attack can't magic up a password that isn't in the candidate list); A/B/C use the
same people so the comparison is fair; changing a salt invalidates a cached
table; the full pass shows the expected per-salt counts. The grader recomputes
every count itself — self-reported numbers don't count.

## Bonus — lookup table vs a *real* rainbow table

The lecture name-dropped rainbow tables; here's where you build one and see why
it's cleverer than "store every hash". Using a small 1,024-word domain, SHA-256
and the provided scaffolding (`P`, `hash_hex`, `reduce_fn`, `walk_chain`), build:

- a **full lookup table** (every `digest → password`) — simple, huge;
- a **rainbow table** that stores only chain *starts and endpoints*, using the
  position-dependent reduction `R_i(h) = P[(int(h)+i) mod 1024]`, and recomputes
  chains at lookup time. Implement the build and the lookup/verify.

```bash
python -m bonus.grade --module student.bonus_stub
```

You won't get 100% coverage (chains merge — that's expected and fine). You're
graded on correctness, how much smaller the rainbow table is than the full
lookup, the recomputation it trades for that, and the reuse observation — try a
*salted* target against your table and watch it miss. That miss is the lecture's
one-liner, earned.
