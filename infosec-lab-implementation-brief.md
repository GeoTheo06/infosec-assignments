# Information Security practicals: implementation brief

Prepared 16 October 2026. Audience: the TA or developer implementing the labs.

This specifies five exercises, their student workflows, the components to build, and acceptance checks. It is an engineering handoff, not a claim that the five lab environments have already been implemented. The public Wi-Fi fixture and its small dictionary have been downloaded and verified locally; the remaining environments are proposed implementations.

## Decisions already fixed

- Wi-Fi is an offline exercise using a public teaching capture. No student radio hardware, live capture, deauthentication, or WPA3 test network is required. Protection-mode comparisons are explanatory questions.
- The imitation page uses a fictional reference site and disposable lab credentials. We prepare publishing and collection.
- DH uses an ordinary active MITM with two separate shared secrets. The student must read, change, re-encrypt, and forward a message. Do not substitute the simpler parameter-injection/key-fixing attack.
- Passwords and accounts in the benchmark are synthetic. The lookup/rainbow-table exercise is a bonus.
- JWT includes both a working attack and a small code repair. Students use a supported library; the flaw is intentional application misuse.

## Shared delivery approach

Use a prepared Linux workspace containing a browser, terminal, Wireshark, Aircrack-ng, Python and pinned Python dependencies. A hosted desktop avoids Windows/macOS installation differences. Browser-only access is sufficient for imitation and JWT; notebooks or small API clients support DH and passwords. Providing a VM is an alternative if hosted desktops are unavailable.

Each exercise needs a short student handout, starter files, TA reference solution, automated checker, reset procedure and dependency/version manifest. Keep teacher answer keys and signing/private keys out of student packages. Existing course accounts can supply group identity; there is no need to build a new identity platform.

For dynamic exercises, bind events to the authenticated group and run/session, not a group identifier supplied by the attacker. Student repair code should run separately from the grader's secrets and expected answers. Use a fresh instance or fixture for final verification.

| Exercise | Main custom implementation | Relative preparation |
|---|---|---|
| Wi-Fi | Package verified fixtures, write questions and checker | Low |
| Imitation page | Reference page, publish integration and browser/event checker | Low–moderate |
| DH MITM | Two peers, interception API, helpers, transcript and grader | Moderate |
| Password benchmark | Fixture generator, instrumented experiment runner and checker | Moderate; bonus adds work |
| JWT | Small application, broken verifier, repair interface and tests | Low |

These levels describe the proposed scope. Infrastructure integration and a classroom pilot remain necessary.

## 1. Wi-Fi PCAP password recovery and traffic decryption

### Exercise and student task

Students receive a recording of a WPA2-Personal connection and a small password list. They identify the network and authentication handshake, recover the weak passphrase, configure Wireshark to decrypt wireless traffic, and answer questions about the newly visible packets. The lesson is offline guessing against a weak WPA2 password and the difference between wireless encryption and additional encryption inside it.

The comparison with PMF, transition mode and WPA3 is text in the assignment plus short questions. It does not require additional captures or physical experiments.

### Selected public fixture, verified

Use Aircrack-ng's official `test/wpa2-psk-linksys.cap`, pinned to commit `7e2256f38f3590af4c19a6ae14ed79bab02242e6`:

[Pinned capture download](https://raw.githubusercontent.com/aircrack-ng/aircrack-ng/7e2256f38f3590af4c19a6ae14ed79bab02242e6/test/wpa2-psk-linksys.cap)

| Property | Verified value |
|---|---|
| File size | 44,717 bytes |
| Packet count | 499 |
| SHA-256 | `e6a3a0f4ef454d5f881964220fe9f0e19dd9ab1c867f86bf0f85a25b416baccf` |
| SSID | `linksys` |
| Passphrase, TA answer | `dictionary` |
| BSSID | `00:0b:86:c2:a4:85` |
| Complete handshake examples | Frames 50, 51, 53, 54; also 89, 90, 92, 93 |
| Example decrypted ping | Frame 56: `172.16.0.101` to `172.16.0.1`; reply in 57 |
| Example extracted data bytes | `4448435043`, ASCII `DHCPC`, in frame 56's `data.data` field |
| Other decrypted traffic | ARP and outer IP/ESP packets |

Aircrack-ng documents this as a test capture with password `dictionary`. [Upstream sample descriptions](https://www.aircrack-ng.org/doku.php?id=aircrack-ng)

This is a public software test fixture with documented credentials. Local inspection found decrypted ICMP, ARP and ESP traffic, rather than HTTP downloads or a credential-bearing application exchange. Package the exact pinned file and its upstream notice. Students only analyze the capture offline; the task does not involve contacting the historical addresses.

**Important content limitation:** this sample has no HTTP secret to extract. Ask for ping addresses, request/reply frames, payload bytes and recognition of ESP as an additional encryption layer. Do not promise an HTTP password or decrypted HTTPS. A future HTTP-secret version would require a different validated capture.

### Wordlist and resource bound

Use the first 10,000 lines of the RockYou archive from SecLists, pinned to commit `f1196104c5594a19d78b486c52c0794b9d947993`:

[Pinned source archive](https://raw.githubusercontent.com/danielmiessler/SecLists/f1196104c5594a19d78b486c52c0794b9d947993/Passwords/Leaked-Databases/rockyou.txt.tar.gz)

In that exact source order, `dictionary` is line **7,233**. It was the **2,281st candidate** after filtering to the 8–63-byte WPA passphrase length range. The provided 10,000-line LF-normalized excerpt has SHA-256 `906cf174f24d8dafad719faf4ff2a8b8f81011e7f669d93599dbed2087a93395`.

A local single-process Python reference check recovered it in approximately **5.455 seconds**, verifying each eligible candidate against the actual WPA2 EAPOL MIC. That is one CPU measurement, not an Aircrack-ng performance guarantee. The correct password passed and a wrong password failed. Wireshark/TShark 4.0.4 also successfully decrypted the file.

Distribute the excerpt directly. Students do not need the full RockYou archive or a GPU. Keep the known password in TA material; a public sample can be looked up, so the password alone is not sufficient assessment evidence.

### Implementation required from us

1. Vendor the pinned capture, wordlist excerpt and upstream notices in the course package.
2. Preinstall Aircrack-ng and Wireshark. Set a clean Wireshark profile so cached keys do not expose traffic before the student's decryption step.
3. Give the Aircrack-ng command structure and a Wireshark walkthrough, without filling in the recovered password. Example teacher command:

   ```sh
   aircrack-ng -w rockyou-first-10000.txt -e linksys wpa2-psk-linksys.cap
   ```

4. Explain entering a `wpa-pwd` key in Wireshark as `password:SSID`. The full handshake and encrypted data must remain in the capture. [Wireshark instructions](https://www.wireshark.org/docs/wsug_html_chunked/Ch80211Keys.html)
5. Implement a JSON-answer checker and an answer key tied to the pinned file hash. Suggested fields: `ssid`, `bssid`, `password`, `handshake_frames`, `ping_request_frame`, `ping_reply_frame`, `ping_source`, `ping_destination`, `payload_hex`, `remaining_encryption_protocol`.
6. Write the short comparison section below and two or three interpretation questions. It can be checked with structured answers plus one short manually reviewed explanation.

### Comparison text that must be technically correct

- **WPA2-Personal:** a suitable captured handshake allows offline testing of password guesses. The password is not transmitted in plaintext.
- **WPA2 with PMF:** PMF protects certain management frames, including established-connection deauthentication handling. It does **not** stop offline guessing against an already captured suitable WPA2 handshake. A legitimate client join can still be captured. Do not write that PMF makes this entire lab impossible.
- **Transition mode:** it supports WPA2-PSK and WPA3-SAE connections. The result depends on what the particular client negotiated. A WPA2 connection still has the corresponding WPA2 exposure. Recovering a shared password from that connection does not reveal old SAE session keys.
- **WPA3-Personal/SAE:** the same passive WPA2 capture-and-dictionary method does not apply. Even knowing the network password and recording the four-way handshake is insufficient for Wireshark decryption of an SAE session; endpoint session key material is needed.

Sources: [Wireshark WPA3 decryption](https://www.wireshark.org/docs/wsug_html_chunked/Ch80211Keys.html), [HPE Aruba WPA3 and transition mode](https://arubanetworking.hpe.com/techdocs/aos/wifi-design-deploy/security/modes/wpa3-personal/).

### Acceptance checks

- A fresh workspace initially shows the relevant data as protected; entering the recovered key reveals the specified packets.
- The short dictionary recovers the known passphrase within the pilot's published resource limit.
- The grader accepts alternative complete handshake sets, not only one hard-coded four-frame sequence.
- Correct packet evidence is required alongside the password. The publicly documented password is not an individualized flag.

**Student setup:** open the prepared desktop and supplied files. No capture adapter, monitor mode or live wireless operation.

## 2. Imitation login page

### Exercise and student task

Students reproduce a supplied fictional login page, using AI coding, a page editor or a site-import tool. They publish it to their assigned lab address, demonstrate that a dummy submission reaches the collector, and explain the copied trust cues and actual origin/submission destination. This is a small introductory exercise about convincing appearance and website identity.

### Recommended implementation

Use **GoPhish for landing-page serving and capture**, plus a small publishing integration. We build the reference page and the simplified student workflow. A full email campaign is outside the assessed task.

GoPhish already supports importing HTML, creating landing pages and capturing submissions. Its campaign API exposes event payloads. [Landing-page API](https://docs.getgophish.com/api-documentation/landing-pages), [campaign API](https://docs.getgophish.com/api-documentation/campaigns).

### Implementation required from us

1. **Reference portal:** one static HTML/CSS page for a fictional organization, with a logo, colors, labels and a working-looking login form. Host assets on course infrastructure and provide them as a download. Keep it simple enough to recreate without a frontend build system.
2. **Serving and collection:** deploy pinned GoPhish instances, preferably isolated per group. Keep management access separate from the published page origin. Use course-managed HTTPS addresses or a prepared local browser environment.
3. **Prepared campaign infrastructure:** one synthetic recipient per group and local SMTP delivery to a test inbox such as Mailpit. This initializes GoPhish's tracked campaign URLs; students need not send email. [Mailpit](https://mailpit.axllent.org/docs/)
4. **Minimal publish workflow:** accept a single HTML file with inline CSS and links to the supplied assets; create/update a landing page via the API, enable dummy-data capture and return a tracked recipient URL. Create a fresh campaign/version on each publication so the tested page is the version the student just submitted.
5. **Import option:** if offering site import, expose the supplied reference URL as a button. We do not need a general-purpose website crawler or full JavaScript-app cloning.
6. **Form starter:** supply a POST form with username/password fields and empty action, so it posts back to the GoPhish page. Both inputs need names and the relevant capture options enabled. Students may change the presentation. [GoPhish form requirements](https://docs.getgophish.com/user-guide/faq)
7. **Result view:** show the group's dummy submission events in a simple status panel or through its isolated GoPhish UI.
8. **Browser grader:** visit the published tracked URL, fill a fresh random dummy username/password, submit, and confirm the corresponding event through the management API. Run this browser without teacher/admin sessions or credentials.

The initial release can use existing GoPhish UI for editing and a TA-provided publish script instead of a custom editor. A course portal integration only needs HTML upload, publish and results operations. It does not need accounts, DNS purchase or hosting accounts for students.

### Student workflow

1. Inspect the reference and decide which details to reproduce.
2. Create/import the page and retain a working form.
3. Upload and publish it using the provided workflow.
4. Use the tracked test URL, rather than only the editor preview, to submit the dummy marker.
5. Inspect the collector result and explain two convincing visual details, the actual page origin and the submission destination.

### Grading and acceptance checks

- Automatic: published page loads, form can be used, and the fresh exact dummy values reach the correct group's collector. Check the deployed page version.
- Manual, small allocation: visual resemblance and explanation of trust cues. A successful bot submission does not measure human persuasiveness.
- A copied visual page with a broken form must fail functionality checks; a working generic form does not receive full visual/explanation credit.
- All mail and submissions are course test traffic. Students never need to collect a classmate's real password.

**Student setup:** browser and optional editor/AI coding tool. We provide the URL, assets and publishing system; students do not configure SMTP or GoPhish servers.

## 3. Unauthenticated Diffie–Hellman MITM with message alteration

### Exercise and student task

Alice and Bob establish an encryption key without authenticating their exchanged public values. The student sits between them and replaces those values with two attacker-generated public values. Alice shares one secret with the attacker; Bob shares another. The student decrypts Alice's message, changes specified fields, re-encrypts it for Bob and delivers it successfully.

The lesson is missing peer authentication. Students do not recover either peer's private exponent and do not break the encryption algorithm.

### Existing foundation and implementation choice

[Cryptopals Challenge 34](https://cryptopals.com/sets/5/challenges/34) is a useful related specification and explicitly permits simulation. Its main parameter-injection attack is **not** our assessed attack. Use valid public values and two attacker exponents.

Implement a small Python service with `cryptography` for HKDF and AES-GCM, and a supplied Python client/notebook. Python's integer modular exponentiation is sufficient for classic DH. No real packet interception, ARP spoofing or proxy configuration is needed.

### Protocol contract

Use the fixed 2048-bit MODP group 14 from [RFC 3526, section 3](https://www.rfc-editor.org/rfc/rfc3526.html#section-3), generator `g = 2`, and `q = (p - 1) / 2`. Generate fresh private exponents from the subgroup range using `secrets`. Keep peer state in the service process.

Let Alice's public value be `A = g^a mod p` and Bob's be `B = g^b mod p`. The attacker chooses fresh private exponents `x` and `y`, sends `g^x mod p` to Alice and `g^y mod p` to Bob, and computes:

```text
secret_with_Alice = A^x mod p
secret_with_Bob   = B^y mod p
```

These match what Alice and Bob compute, respectively. Validate incoming public values: exclude trivial/invalid values and require subgroup membership. This keeps the exercise focused on authentication rather than deliberately weak parameters.

Derive a 32-byte encryption key using HKDF-SHA256 from the fixed-width shared-secret bytes. Fix the serialization, salt and context in the supplied helper: for example, 256-byte big-endian secret; SHA-256 of session ID as salt; `infosec-dh-lab-v1` as context. Both peers and the student helper use the same documented function. [HKDF documentation](https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#hkdf)

Use AES-GCM with fresh 12-byte nonces. Bind the session ID as associated data and include it in the message. Authenticated encryption still permits this MITM: the attacker legitimately knows each leg's different key and creates a valid new tag. [AES-GCM API](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM)

### Message and target

Alice's plaintext is structured JSON, for example:

```json
{
  "session_id": "<fresh session ID>",
  "recipient": "lab-account-A",
  "amount": 10,
  "memo": "<fresh random value>"
}
```

The assignment tells the student to change `recipient` to `lab-account-B` and `amount` to `900`, preserving the other fields. The fresh unknown memo means inventing a replacement without decrypting Alice's message does not satisfy the task. Only dummy operations occur.

### Implementation required from us

1. **Peer service:** Alice/Bob state, private exponents, public values, key derivation, encryption and Bob's actual receive/decrypt operation.
2. **Interception API**, with a minimal contract:
   - `POST /sessions`: create a fresh run; return ID, fixed parameters, public `A`/`B`, and the required change.
   - `POST /sessions/{id}/substitute`: accept `to_alice` and `to_bob`; establish the two legs and return Alice's encrypted packet.
   - `POST /sessions/{id}/deliver`: accept the attacker's nonce/ciphertext; let Bob decrypt and validate it; return a receipt/event ID.
3. **Packet format:** JSON with Base64 nonce and ciphertext-with-tag; associated data is derived from the documented session ID, not freely trusted request data.
4. **Student client/helpers:** modular-exponentiation wrapper, fixed encoding, HKDF and AES-GCM encrypt/decrypt. Provide transport/error handling. Leave choice of attacker values, use of the two secrets and message modification to students.
5. **Transcript:** record the original and substituted public values plus send/receive events. Show public events to students; do not return peer private exponents, expected plaintext or derived keys.
6. **Grader:** create fresh sessions, run a submitted attack function against the API, and inspect Bob's received plaintext in private grader state. The function can use supplied helpers but cannot import peer internals.

### Student workflow and acceptance checks

Observe a normal exchange; replace public values; derive both secrets; recover Alice's full plaintext; make the specified change; re-encrypt under Bob's key; deliver and identify the receipt.

Check that a normal relay delivers the original message; a ciphertext-only byte edit fails GCM verification; the full MITM succeeds; and fresh session values do not break a correct submitted attack. Bob must receive the target fields **and the original memo/session ID**. A printed claim or student-submitted plaintext is not sufficient.

A short explanation can ask why authenticating the exchange with already trusted signing keys prevents substitution. Implementing that repair is optional, not required for this version.

**Student setup:** supplied notebook/client in the prepared workspace. No network configuration or implementation of DH arithmetic/AES from scratch.

## 4. Password-database breach benchmark

### Exercise and student task

Students recover synthetic passwords from four equivalent storage schemes. They measure the work that can be reused across accounts and across database releases, then compare cheap hashing with deliberately expensive password derivation. They must distinguish salts, password strength and cost per guess.

This can be an offline package. There is no need for a vulnerable website, SQL injection or a stolen real database.

### Recommended implementation and exact schemes

Use Python `hashlib` for the authoritative experiment runner. It supplies SHA-256 and PBKDF2-HMAC-SHA256 without another password-hashing package. PBKDF2 satisfies the requested expensive-KDF comparison; bcrypt is a possible substitute, not a requirement. [Python hashlib](https://docs.python.org/3/library/hashlib.html)

| Dataset | Exact construction |
|---|---|
| A: unsalted | `SHA256(password_bytes)` |
| B: shared salt | `SHA256(password_bytes || salt_bytes)`; one public salt for all rows |
| C: individual salts | The same SHA-256 construction; a different public salt for every row |
| D: expensive KDF | `PBKDF2-HMAC-SHA256(password_bytes, salt_bytes, iterations, dklen=32)`; individual salts |

Define encoding unambiguously: candidate passwords are ASCII; salts are 32-character ASCII hex strings generated from 16 random bytes, and those **displayed ASCII characters** are hashed directly, rather than hex-decoded. Store digest hex and parameters in JSON/CSV. The format is intentionally easy to inspect.

If we want existing cracking-tool practice, export A as Hashcat mode 1400, B/C as mode 1410 (`digest:salt`), and D as mode 10900 with the appropriate Base64 salt/digest fields. Supply and test the export/conversion script. Hashcat documents all these modes. [Hashcat formats](https://hashcat.net/wiki/doku.php?id=example_hashes)

### Fixtures and resource budget

For the fast-hash experiment, start with 12 synthetic accounts and a fixed ordered list of 512 distinct candidate passwords. Include repeated passwords across accounts and some account passwords outside the candidate list. Use the same underlying account/password selection in A–C to make comparisons meaningful. Generate a second database release to test table reuse.

For D, use a small, separate paired benchmark: two accounts and 128 candidates, with several iteration counts. Calibrate a count such as 50,000 on the actual course CPU before release and bound the total run to a few minutes. This is an experimental teaching setting, not a production password policy. Students do not need to exhaust a full RockYou list against a slow KDF.

Avoid judging an independent cracking run by reusing passwords learned from another dataset. The runner should start each comparison afresh and count actual candidate evaluations; comparing algorithms on the same known inputs is fine, but one verification of an already recovered password is not a new password search.

### Implementation required from us

1. **Fixture generator:** group seed, synthetic account IDs, passwords sampled from a bounded pool, repeated-password cases, salts, digest files and a private answer manifest. Regenerate salts without changing the intended difficulty.
2. **Candidate-list package:** fixed order, encoding, size and a few intentionally absent passwords. Supply it rather than requiring unrelated wordlist research.
3. **Instrumented runner:** candidate generation, hashing, grouping targets by salt, matching, counters and JSON results. Students choose strategies and complete a few small functions rather than write parsing or crypto implementations.
4. **Two experiment modes:**
   - Recovery mode stops when appropriate and records which accounts were recovered.
   - Controlled full-pass mode evaluates all `D` candidates for every distinct salt context, avoiding early-stop/password-rank noise.
5. **Reuse experiment:** build results for release 1, then try release 2 with no salt, the same shared salt, a changed shared salt and new individual salts. A shared-salt table is reusable only when that salt matches.
6. **Benchmark harness:** monotonic timer, fixed CPU allocation for comparable measurements, reported iteration counts and repeated timing samples. CPU time is an observation, not the primary grade.
7. **Answer/strategy grader:** validate recovered accounts against fixtures and rerun small submitted strategy functions on unseen fixtures. Recompute work counts in the trusted harness instead of accepting self-reported speed or counters.

For a full-pass experiment with 12 targets, 512 candidates and all individual salts distinct, a grouped implementation should require 512 digest evaluations for A, 512 for B, and 6,144 for C, plus comparisons. D also has per-salt candidate work, with much greater work inside each derivation. A naive repeated per-account implementation can do more work; students should investigate why.

### What students submit

Recovered account/password mappings, runner output, their small strategy functions, a table of evaluation counts and timing observations, and short answers explaining reuse. A salt is public and does not stop testing weak candidates; it changes how effectively guesses can be amortized.

### Acceptance checks

Known in-list passwords are recoverable; out-of-list passwords remain unresolved in the bounded attack; equivalent inputs are used for comparisons; changing a salt invalidates a cached context; and the runner demonstrates the expected salt-context counts. Pilot D independently so its cost cannot stall the entire assignment.

**Student setup:** prepared Python notebook/terminal. Hashcat is optional and preinstalled if used; a GPU is unnecessary.

### Bonus: full lookup tables versus genuine rainbow tables

Use a much smaller closed password domain, such as 1,024 synthetic words, SHA-256 and provided scaffolding. Do not attempt full-scale RockYou rainbow tables.

Students first create a full mapping from digest to candidate. Then build a rainbow table that stores chain starts and endpoints. Each chain repeatedly hashes a candidate and uses a **position-dependent reduction function** to select another candidate from the domain. Lookup tries possible positions, follows to endpoints, then regenerates a matching chain to verify the password. Storing every digest/candidate pair is a lookup table, not a rainbow table. [Oechslin's original paper](https://www.iacr.org/archive/crypto2003/27290615/27290615.pdf)

We provide the chain-walking/search loop, encoding, counters and deterministic reduction helper. For example, with ordered domain `P`, use `R_i(h) = P[(integer(h) + i) mod len(P)]`. Student functions build the start/end table and recover or verify candidates. Keep duplicate endpoints as multiple possible starts.

Choose small chain lengths and counts in the pilot, measure actual coverage, and generate some guaranteed-covered and some uncovered test targets. Full recovery is not guaranteed because chains merge and coverage is partial. Grade correctness, stored entries, recomputation and reuse observations rather than demanding 100% coverage.

Repeat lookup against a new unsalted release, the same shared-salt context and a different salt. Explain why individual salts require separate context-specific work. A failed reuse does not imply salted passwords cannot be guessed individually.

## 5. JWT privilege escalation and verifier repair

### Exercise and student task

Students log in as an ordinary user and receive a signed JWT. The intentionally broken server reads its claims without verifying the signature. Students change the role or identity and demonstrate access to a protected lab endpoint. They then repair one verification function, keeping genuine tokens usable.

Use a small Python web application plus PyJWT and `cryptography`. Juice Shop is a useful attack demonstration, but a small application gives students a clear repair boundary and avoids unrelated application code.

### Token and authorization contract

Use **RS256** for this lab. The issuer's private signing key stays in the backend; students receive the public verification key and normal-user tokens. This also allows the repair to be implemented without giving students signing authority.

Required claims: `iss`, `aud`, `sub`, `role` and `exp`. State their expected types and meanings in the handout. `sub` identifies a synthetic account; `role` is `student` or `admin`. The issuer and audience are fixed by server configuration. Tokens have a short course-friendly lifetime, with a reset/reissue button if they expire.

The lab's protected endpoint trusts the **verified** issuer's role assertion and requires an existing account in the current group. Login always issues the ordinary user's real role; it must not accept a client-selected administrator role. Per-group signing keys simplify isolation.

The broken version deliberately uses PyJWT's unverified decode mode. Do not depend on a vulnerability in an old package version. The repaired version must use the configured public key, fixed allowed algorithm, expected issuer/audience, required claims and expiry verification. PyJWT warns against choosing allowed algorithms from attacker-controlled token headers. [PyJWT API](https://pyjwt.readthedocs.io/en/latest/api.html), [unverified decoding](https://pyjwt.readthedocs.io/en/latest/usage.html#reading-the-claimset-without-validation)

### Implementation required from us

1. **Small application:** login, current-user view and an administrator-only operation returning a group/run marker. A simple form/API explorer is enough.
2. **Issuer:** per-instance RSA key pair and token generation. Keep private key access in a separate issuer component/process when running student repair code.
3. **Vulnerable verifier:** decode claims with signature validation disabled and pass them to the same authorization logic used in the repaired version.
4. **Token editor:** show header/payload JSON, Base64URL encoding and the original signature. Let students change claims and send the resulting token. Supply this UI or a notebook helper so browser-storage quirks do not dominate the task.
5. **Repair interface**, for example:

   ```python
   def verify_token(token, public_key, expected_issuer, expected_audience):
       """Return validated claims or raise InvalidTokenError."""
   ```

   Give students the surrounding application, key loading, exception handling and tests. They implement validation and the specified claim checks, not RSA or JSON parsing from scratch.
6. **Integration grader:** exercise the verifier and real endpoint behavior. Keep normal-user versus administrator authorization outside the student's editable verifier so validation and permissions can be assessed separately.
7. **Reset/reissue:** fresh token and instance state without exposing the signing key.

### Student workflow

Log in normally; decode the token; change `role` or `sub` while retaining an invalid original signature; demonstrate unauthorized endpoint access; explain the missing check; repair the verifier; rerun the original attack and legitimate controls.

### Required acceptance tests

| Case | Expected behavior after repair |
|---|---|
| Genuine ordinary-user token | Valid authentication; administrator operation forbidden |
| Genuine administrator token from the trusted test issuer | Administrator operation succeeds |
| Changed role or subject with original signature | Authentication rejected |
| Corrupted signature or wrong signing key | Rejected |
| Unsigned token or unapproved algorithm | Rejected |
| Expired token | Rejected |
| Missing required claim or wrong issuer/audience | Rejected |
| Malformed token or invalid claim types/role | Rejected cleanly |
| Valid token for an unknown or other-group account | No access to the protected group resource |

Use fresh keys/accounts/claims in hidden tests. A verifier that rejects everything must fail the legitimate-token checks. Distinguish invalid authentication (401) from valid authentication with insufficient permission (403).

**Student setup:** browser and prepared code workspace with PyJWT/cryptography installed. No proxy, OAuth provider or external identity service.

## Suggested implementation order and completion criteria

1. Package the verified Wi-Fi exercise and checker.
2. Implement JWT's small application and positive/negative repair tests.
3. Implement the DH service, reference MITM and fresh-session grader.
4. Implement the password generator and controlled counters before tuning slow-KDF runtimes; add the bonus afterward.
5. Connect GoPhish publishing and browser grading, then pilot the imitation-page instructions with a student-created page.

Before releasing any exercise, run it from a fresh student workspace, verify the TA reference solution, verify the intended failed/invalid cases, and confirm that students are not doing configuration outside the stated learning objective. Keep a TA answer key, a student package, reset instructions and a fixture/version manifest for each.

## Wi-Fi validation evidence and reference kit

The accompanying `wifi-reference-kit.zip` is a **TA package**. It contains the exact capture, the 10,000-line wordlist excerpt, source/license notices, checksums, observed packet facts and local verification results. Its README contains the password and answer key; distribute only the intended student files, not the whole TA package.

The other four lab environments have not been built by this brief. Their interfaces and acceptance checks above describe the implementation required.
