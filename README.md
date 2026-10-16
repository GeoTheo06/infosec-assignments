# Information Security practicals — lab implementations

This repository implements the five exercises specified in
[`infosec-lab-implementation-brief.md`](infosec-lab-implementation-brief.md).

Each lab is self-contained under `labs/` and ships the artifacts the brief asks
for: a **student handout**, **starter files**, a **TA reference solution**, an
**automated checker/grader**, a **reset procedure**, and a **version manifest**.

| # | Lab | Directory | Runnable here | Needs infra |
|---|-----|-----------|---------------|-------------|
| 1 | Wi-Fi PCAP recovery & decryption | [`labs/lab1-wifi`](labs/lab1-wifi) | checker + packaging (Aircrack/Wireshark on course image) | — |
| 2 | Imitation login page | [`labs/lab2-imitation`](labs/lab2-imitation) | portal, publish & grader scripts | GoPhish + Mailpit (compose provided) |
| 3 | Unauthenticated DH MITM | [`labs/lab3-dh-mitm`](labs/lab3-dh-mitm) | service, helpers, reference attack, grader, tests | — |
| 4 | Password-breach benchmark | [`labs/lab4-passwords`](labs/lab4-passwords) | generator, runner, reuse, bonus, grader, tests | — |
| 5 | JWT privilege escalation & repair | [`labs/lab5-jwt`](labs/lab5-jwt) | app, vulnerable+repaired verifier, grader, tests | — |

## Repository layout

```
infosec-assignments/
├─ README.md                         ← this file
├─ infosec-lab-implementation-brief.md
├─ wifi-reference-kit.zip            ← original TA kit (source of lab 1 fixtures)
├─ workspace/                        ← shared dependency/version manifest + setup
└─ labs/
   ├─ lab1-wifi/        student/  ta/  checker/
   ├─ lab2-imitation/   reference-portal/  publish/  grader/  infra/  student-starter/
   ├─ lab3-dh-mitm/     service/  student/  ta/  grader/  tests/
   ├─ lab4-passwords/   passlab/  student/  ta/  grader/  tests/
   └─ lab5-jwt/         app/  student/  ta/  grader/  tests/
```

## Conventions used across labs

- **Secret hygiene.** Teacher answer keys, signing private keys and expected
  plaintext never ship in a student package. Each lab documents exactly which
  files are student-facing vs. TA-only.
- **Group/run binding.** Dynamic exercises (2, 3, 5) bind events to an
  authenticated group/session that the server controls, never to an identifier
  supplied by the attacker side. Run IDs here are placeholders where no real
  identity platform is wired in; the integration points are documented.
- **Fresh instances for verification.** Graders create a fresh fixture/session
  and re-run the submitted student code against it, recomputing work counts in
  trusted harness state rather than trusting self-reported results.
- **Pinned dependencies.** See [`workspace/requirements.txt`](workspace/requirements.txt).

## Quick start (developer / TA)

```bash
# 1. Create the workspace environment (Python 3.11+)
python -m venv .venv
. .venv/Scripts/activate      # Windows;  use .venv/bin/activate on Linux/macOS
pip install -r workspace/requirements.txt

# 2. Run every lab's test suite (each in its own process — see note below)
python run_tests.py
# ...or one lab at a time (labs are independent packages that reuse names
# like `grader`/`ta`/`student`, so run each from its own directory):
#   cd labs/lab5-jwt && pytest tests -q

# 3. Lab 1 checker (no extra deps):
python labs/lab1-wifi/checker/check_answers.py \
       --key labs/lab1-wifi/ta/answer_key.json \
       --capture labs/lab1-wifi/student/wpa2-psk-linksys.cap \
       labs/lab1-wifi/ta/reference_answers.json
```

See each lab's `README.md` for the student workflow, the TA solution, the reset
procedure and the acceptance checks mapped to the brief.

## Implementation order (from the brief)

1. Wi-Fi packaging + checker → 2. JWT → 3. DH → 4. Passwords → 5. Imitation.
The code here follows that order; labs are independent and may be released
individually.
