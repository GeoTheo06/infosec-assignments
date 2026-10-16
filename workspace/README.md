# Workspace / course image

The brief calls for a prepared Linux workspace (hosted desktop or VM) with a
browser, terminal, Wireshark, Aircrack-ng, Python and pinned Python
dependencies. This directory holds the shared manifest and notes for building
that image; the per-lab runtime details live in each lab's README.

## Python environment

```bash
python -m venv .venv
. .venv/Scripts/activate        # Windows (Git Bash / PowerShell: .venv\Scripts\activate)
# Linux/macOS: . .venv/bin/activate
pip install -r workspace/requirements.txt
```

Verified toolchain: CPython **3.11.4**, packages pinned in
[`requirements.txt`](requirements.txt).

## OS packages (course image)

Installed on the hosted desktop / VM, not via pip:

| Tool | Used by | Notes |
|------|---------|-------|
| `aircrack-ng` | Lab 1 | Dictionary recovery of the WPA2 passphrase. |
| `wireshark` + `tshark` | Lab 1 | 802.11 decryption walkthrough + reproducible CLI check. Verified against 4.0.4. |
| `docker` + `docker compose` | Lab 2 | Runs the pinned GoPhish + Mailpit stack. |
| Chromium/Firefox | Labs 1,2,5 | Browser-only access for imitation and JWT; Wireshark GUI for lab 1. |

## Clean Wireshark profile (lab 1)

Ship a Wireshark profile with **no** preloaded 802.11 decryption keys so cached
keys do not reveal traffic before the student performs the decryption step. See
[`../labs/lab1-wifi/README.md`](../labs/lab1-wifi/README.md).

## Secret hygiene

- Student packages are produced by each lab's packaging step and exclude TA
  answer keys and any signing/private keys.
- The JWT issuer private key and DH peer private exponents are generated at
  runtime inside the server process and never written into student-facing files.
