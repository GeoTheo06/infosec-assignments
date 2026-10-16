# Lab 1 — Wi-Fi PCAP password recovery and traffic decryption

Offline exercise built on Aircrack-ng's official public test capture. Students
recover a weak WPA2 passphrase from a small dictionary, decrypt the wireless
traffic in Wireshark, and answer packet-evidence questions.

## Contents

```
lab1-wifi/
├─ student/                 ← ships to students
│  ├─ wpa2-psk-linksys.cap        pinned capture (44,717 B)
│  ├─ rockyou-first-10000.txt     10,000-line wordlist excerpt
│  ├─ AIRCRACK-NG-LICENSE.txt     upstream notices
│  ├─ SECLISTS-LICENSE.txt
│  ├─ HANDOUT.md                  student instructions + reading + questions
│  └─ answers.template.json       answer sheet to fill in
├─ checker/check_answers.py  ← stdlib checker (ships with student pkg; key stays server-side)
├─ ta/                       ← TA ONLY — never ship
│  ├─ answer_key.json              bound to capture sha256; accepts alt handshake/ping sets
│  ├─ reference_answers.json       a correct submission (uses alternative sets)
│  ├─ negative_answers.json        right password, wrong evidence → must fail
│  ├─ TA-README.md                 full answer key (from the verified kit)
│  └─ verification.json            observed packet facts + checksums
├─ make_student_package.py   ← builds lab1-wifi-student.zip, excludes ta/
└─ README.md
```

## Pinned fixture (verified)

| Property | Value |
|---|---|
| Capture | Aircrack-ng `test/wpa2-psk-linksys.cap` @ `7e2256f3…` |
| SHA-256 | `e6a3a0f4ef454d5f881964220fe9f0e19dd9ab1c867f86bf0f85a25b416baccf` |
| SSID / BSSID | `linksys` / `00:0b:86:c2:a4:85` |
| Passphrase (TA) | `dictionary` (wordlist line 7,233; 2,281st eligible candidate) |
| Wordlist excerpt SHA-256 | `906cf174f24d8dafad719faf4ff2a8b8f81011e7f669d93599dbed2087a93395` |

Checksums re-verified in this repo; both files match the kit's `SHA256SUMS.txt`.

## TA reference solution

The full answer key is in [`ta/TA-README.md`](ta/TA-README.md) and
[`ta/answer_key.json`](ta/answer_key.json). Valid complete handshakes:
`{50,51,53,54}`, `{89,90,92,93}`, `{339,340,343,344}`. Valid ICMP pairs:
`56/57`, `285/286`, `346/347`. Frame 56 `data.data` = `4448435043` (`DHCPC`).
Inner still-encrypted layer = **ESP**.

## Running the checker

```bash
# correct submission (alt handshake set + alt ping pair) -> PASS
python checker/check_answers.py --key ta/answer_key.json \
    --capture student/wpa2-psk-linksys.cap ta/reference_answers.json

# right password but wrong packet evidence -> FAIL (password alone is not enough)
python checker/check_answers.py --key ta/answer_key.json \
    --capture student/wpa2-psk-linksys.cap ta/negative_answers.json
```

The checker refuses to grade if the supplied capture's SHA-256 does not match
the key, so answers must come from the official fixture.

## Build the student package

```bash
python make_student_package.py -o lab1-wifi-student.zip
```

The script hard-fails if any `ta/` artifact would be included.

## Acceptance checks (brief → implementation)

| Brief requirement | How it's met |
|---|---|
| Fresh workspace shows data protected until the key is entered | Ship a clean Wireshark profile with no 802.11 keys (see `workspace/README.md`); capture retains full handshake + encrypted data. |
| Short dictionary recovers passphrase within resource bound | Password is line 7,233 / 2,281st eligible; reference MIC check ran in ~5.455 s single-process (`ta/verification.json`). |
| Grader accepts alternative complete handshake sets | `answer_key.json` `one_of_sets`; `reference_answers.json` uses the 2nd set. |
| Packet evidence required alongside password | `required_for_pass` includes handshake/ping/payload/ESP; `negative_answers.json` (correct password, bad evidence) fails. |
| PMF/transition/WPA3 comparison technically correct | `student/HANDOUT.md` reading section matches the brief's required wording. |

## Reset procedure

The exercise is read-only against immutable fixtures, so "reset" = re-extract a
fresh copy of `student/` and load the clean Wireshark profile (no cached keys).
Nothing student-side persists. Re-verify integrity any time:

```bash
sha256sum student/wpa2-psk-linksys.cap student/rockyou-first-10000.txt
```

## Content limitation (important)

This capture has **no** HTTP/application secret and no decrypted HTTPS. Questions
ask for ping addresses, request/reply frames, payload bytes, and recognition of
ESP as an additional encryption layer. Do not promise an HTTP password. A future
HTTP-secret variant would need a different validated capture.
