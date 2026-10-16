# Fixture & dependency manifest

One place to see what is pinned per lab. Student packages exclude everything
marked TA-only.

## Toolchain

| Component | Version |
|-----------|---------|
| Python | 3.11 (developed on 3.11.4) |
| cryptography | 44.0.0 |
| PyJWT | 2.10.1 |
| Flask | 3.1.0 |
| requests | 2.32.3 |
| pytest | 8.3.4 |
| GoPhish (lab 2) | built from source @ tag v0.12.1 (no official image) |
| Mailpit (lab 2) | axllent/mailpit:v1.31.6 |
| Aircrack-ng / Wireshark (lab 1) | course-image OS packages; verified against TShark 4.0.4 |

Pins live in [`workspace/requirements.txt`](workspace/requirements.txt) and
[`labs/lab2-imitation/infra/docker-compose.yml`](labs/lab2-imitation/infra/docker-compose.yml).

## Lab 1 — Wi-Fi fixtures (verified)

| Artifact | SHA-256 |
|----------|---------|
| `wpa2-psk-linksys.cap` (44,717 B, 499 pkts) | `e6a3a0f4ef454d5f881964220fe9f0e19dd9ab1c867f86bf0f85a25b416baccf` |
| `rockyou-first-10000.txt` | `906cf174f24d8dafad719faf4ff2a8b8f81011e7f669d93599dbed2087a93395` |

- Capture pinned to Aircrack-ng commit `7e2256f38f3590af4c19a6ae14ed79bab02242e6`.
- Wordlist excerpt from SecLists commit `f1196104c5594a19d78b486c52c0794b9d947993`.
- Passphrase `dictionary` (TA-only): source line 7,233; 2,281st eligible candidate.
- Both files re-verified in this repo against the kit's `SHA256SUMS.txt`.

## Lab 3 — DH parameters

- RFC 3526 MODP group 14 (2048-bit), `g = 2`, `q = (p-1)/2`.
- Verified: `pow(2, q, p) == 1` (g=2 generates the order-q subgroup), so the
  `pow(v, q, p) == 1` public-value check is exact.
- HKDF context `infosec-dh-lab-v1`; 256-byte big-endian secret; AES-GCM 12-byte
  nonce; AAD = session id.

## Lab 4 — fixtures

- 512 fixed-order candidates (`passlab.candidates`, content-addressed).
- Main benchmark: 12 accounts; full-pass evaluation counts **A=512, B=512,
  C=6144**. Scheme D small fixture: 2 accounts × 128 candidates.
- Bonus domain: 1024 words; reduction `R_i(h)=P[(int(h)+i) mod 1024]`.

## Lab 5 — JWT

- RS256, fresh 2048-bit RSA keypair per issuer instance (private key never
  shipped). Claims `iss, aud, sub, role, exp`; roles `student|admin`.

## TA-only files (never ship to students)

```
labs/lab1-wifi/ta/*                      (answer key, TA readme, verification.json)
labs/lab3-dh-mitm/ta/reference_attack.py
labs/lab4-passwords/ta/reference_strategy.py
labs/lab4-passwords/bonus/reference.py
labs/lab5-jwt/ta/verifier_solution.py
labs/lab2-imitation/infra/*  + the GoPhish admin API key
```

Lab 1 ships via `labs/lab1-wifi/make_student_package.py` (hard-fails if a TA
artifact would be included).
