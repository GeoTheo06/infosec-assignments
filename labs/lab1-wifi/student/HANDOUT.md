# Lab 1 — Breaking into a Wi-Fi recording (offline)

Someone sat in a café in 2007 and recorded 90 seconds of "secure" Wi-Fi
traffic. No password was ever transmitted. You weren't there, you have no
antenna, and the network is long gone. You're going to read that traffic anyway
— and then hit a wall you *can't* get past, which is the most interesting part
of the whole exercise.

Here's the thing I want you to notice before you start: everything you're about
to do is **offline**. The capture is a dead file. That's exactly what makes it
dangerous — the attacker doesn't need to be near you, doesn't need to rush, and
can keep guessing for as long as they like. Remember the "numbers game" slide
from the Protocols lecture (is 2⁶³ big enough?)? This is that slide, made real,
with a password weak enough to lose the game in seconds.

## Your mission

Take `wpa2-psk-linksys.cap`, recover the Wi-Fi passphrase from a small wordlist,
decrypt the traffic in Wireshark, and answer some questions about what you can
now see — including one layer you *still* can't read even after you win.

**You'll walk away able to:**
- explain why a captured WPA2 handshake lets an attacker guess the password
  *offline*, and why that's different from guessing at the login prompt;
- recognise that breaking one encryption layer doesn't break the ones inside it.

## Where this sits in the course

WPA2's details weren't in a lecture, so here's the 30-second bridge — and notice
it's all stuff you already know under different names:

- The passphrase isn't used as the key directly. WPA2 runs it through
  **PBKDF2**, which is just **HMAC-SHA1 repeated thousands of times** — the same
  HMAC from the Hashing lecture, used as a slow hash. (Sound familiar? It's the
  same idea you'll meet again in Lab 4.)
- The 4-way **handshake** carries a **MIC** (message integrity code) — that's a
  **MAC**, exactly like the lecture's "confirms the message came from someone
  who knows the key". A guessed passphrase is *verified* by recomputing that MAC
  and checking it matches. That's why a recording is enough: each guess is
  checked against the captured MAC, no live network needed.
- WEP, the broken ancestor, used **RC4 + CRC** (both from Crypto 1 / Hashing).
  The lecture called CRC-for-integrity "a fatal flaw" — WPA2 replaced it, which
  is why we're attacking the *password*, not the crypto.

So: offline dictionary attack + MAC verification + key derivation. All course
concepts; just wearing a Wi-Fi hat.

## What you're given

| File | What it is |
|------|------------|
| `wpa2-psk-linksys.cap` | the recorded connection — read-only evidence |
| `rockyou-first-10000.txt` | 10,000 candidate passwords |
| `AIRCRACK-NG-LICENSE.txt`, `SECLISTS-LICENSE.txt` | where the fixtures come from |

This is a real, public test capture. Analyse it offline; don't go poking at any
address you see inside it — those machines are ghosts from 2007 anyway.

## Step 1 — Win the numbers game

```sh
aircrack-ng -w rockyou-first-10000.txt -e linksys wpa2-psk-linksys.cap
```

`-w` is the wordlist, `-e` is the network name, last argument is the capture.
Aircrack needs a complete 4-way handshake in the file to have a MIC to test
against — it'll tell you if it found one. The password is in the list; you don't
need a GPU or the full 14-million-line RockYou. (Ask yourself afterwards: how
long would this have taken if the password had been 12 random characters? That's
the numbers game again.)

## Step 2 — Decrypt in Wireshark

1. Open the capture in Wireshark.
2. **Edit ▸ Preferences ▸ Protocols ▸ IEEE 802.11 ▸ Enable decryption**.
3. Add a decryption key of type **`wpa-pwd`** with value `password:SSID`:

   ```
   <your recovered password>:linksys
   ```

4. Apply. Frames that were opaque now unfold into ARP, IP, ICMP… and ESP.

Terminal equivalent, if you'd rather (once TShark is installed):

```sh
tshark -r wpa2-psk-linksys.cap -o wlan.enable_decryption:TRUE \
  -o 'uat:80211_keys:"wpa-pwd","<password>:linksys"' \
  -Y icmp -T fields -e frame.number -e ip.src -e ip.dst -e icmp.type
```

## Step 3 — Answer the questions

Fill in `answers.json` (template provided):

| Field | What to put |
|-------|-------------|
| `ssid`, `bssid` | the network name and the access point's MAC |
| `password` | what you recovered |
| `handshake_frames` | the four frame numbers of **one** complete 4-way handshake |
| `ping_request_frame` / `ping_reply_frame` | a matching decrypted ICMP echo pair |
| `ping_source` / `ping_destination` | the IPs in that request |
| `payload_hex` | the `data.data` bytes of the ping request (hex) |
| `remaining_encryption_protocol` | the thing that's **still encrypted** after you decrypted the Wi-Fi |
| `explanation` | your answer to the question below |

Sanity-check your formatting locally:

```sh
python ../checker/check_answers.py --key <TA key> --capture wpa2-psk-linksys.cap answers.json
```

(During grading the checker runs against the hidden key. Note: handing in the
password alone won't pass — it's a public fact. The packet evidence is what
shows you actually did the work.)

## The wall (this is the point of the lab)

Once decrypted, you'll see **ESP** packets you still can't read. You own the
Wi-Fi password — why doesn't that help? Because ESP is a *second* encryption
layer (an IPsec tunnel) with its own keys, negotiated end-to-end between the two
machines. Cracking the café's Wi-Fi password gets you onto the hop; it gets you
nothing inside the tunnel. One broken layer ≠ all layers broken.

Answer in your write-up (this is the graded reasoning):

1. You decrypted the Wi-Fi and still can't read the ESP traffic. What key
   material would you need, and why isn't the Wi-Fi passphrase it?
2. "Just turn on PMF and nobody can crack our Wi-Fi password." What's true and
   false about that? (Hint: PMF protects some management frames; does it stop an
   attacker capturing a legitimate join and guessing offline?)
3. If this network were WPA3-Personal (SAE) instead, which step of your attack
   breaks, and why?

Short reading to back up #2 and #3:

- **WPA2-Personal:** a captured handshake → offline guessing. Password never
  sent in the clear.
- **WPA2 + PMF:** protects certain management frames (e.g. deauth handling). Does
  **not** stop offline guessing against an already-captured handshake.
- **Transition mode:** offers WPA2 *and* WPA3; a client that joined with WPA2
  still has the WPA2 exposure. Cracking that password reveals no WPA3/SAE keys.
- **WPA3-Personal / SAE:** the passive "capture + dictionary" trick does **not**
  apply — even knowing the password and recording the handshake isn't enough to
  decrypt an SAE session.

## Hand in

- `answers.json`, filled in.
- A short write-up with the three answers above.
- Optional: a Wireshark screenshot of your decrypted ping pair.

Think-like-an-attacker, from the GPG lecture: *what did the attacker have to
control to pull this off?* (Answer: almost nothing — just 90 seconds of radio,
once.) That's the lesson.
