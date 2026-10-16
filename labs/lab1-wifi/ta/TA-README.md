# Wi-Fi reference kit — TA material

This package accompanies infosec-lab-implementation-brief.md. It contains answers.
Give students only the capture, the small wordlist and the student instructions.

## Selected fixture

Official Aircrack-ng test/wpa2-psk-linksys.cap, pinned at commit
7e2256f38f3590af4c19a6ae14ed79bab02242e6.

https://raw.githubusercontent.com/aircrack-ng/aircrack-ng/7e2256f38f3590af4c19a6ae14ed79bab02242e6/test/wpa2-psk-linksys.cap

SSID: linksys
Password: dictionary
BSSID: 00:0b:86:c2:a4:85
Capture size: 44,717 bytes; 499 packets.
SHA-256: e6a3a0f4ef454d5f881964220fe9f0e19dd9ab1c867f86bf0f85a25b416baccf

The wordlist is the first 10,000 lines of the pinned SecLists RockYou archive,
LF-normalized. The password is at source line 7,233 and is the 2,281st tested
candidate after filtering to 8–63-byte lengths. Source and checksums are in
verification.json. Upstream repository license notices are included.

## Verification actually performed

A Python PBKDF2-HMAC-SHA1/WPA2 EAPOL MIC checker recovered the password from the
small candidate list in 5.455 seconds on this host. It accepted dictionary and
rejected wrong-password. This is not an Aircrack-ng timing or universal runtime.

TShark/Wireshark 4.0.4 successfully decrypted the capture. Before decryption,
the eapol/arp/ip filter matched 12 packets; after it matched 42: 12 EAPOL,
6 ICMP, 6 ARP and 18 ESP packets. No HTTP/application-secret task is promised.

## Intended student tool command

Run this against the supplied offline fixture in the prepared lab environment:

    aircrack-ng -w rockyou-first-10000.txt -e linksys wpa2-psk-linksys.cap

Aircrack-ng itself was not installed/run during this research. Its command and
runtime should be included in the final course-image acceptance test.

In Wireshark enable IEEE 802.11 decryption and add a wpa-pwd entry:

    dictionary:linksys

A reproducible Linux/macOS terminal decryption check, once TShark is installed:

    tshark -r wpa2-psk-linksys.cap -o wlan.enable_decryption:TRUE -o 'uat:80211_keys:"wpa-pwd","dictionary:linksys"' -Y icmp -T fields -e frame.number -e ip.src -e ip.dst -e icmp.type -e data.data

Use a fresh Wireshark profile without preloaded keys for student work.

## Packet answer key

One full handshake: 50, 51, 53, 54.
Another: 89, 90, 92, 93. Another: 339, 340, 343, 344.
Ping request 56: 172.16.0.101 -> 172.16.0.1; reply 57 reverses those addresses.
Further ping pairs: 285/286 and 346/347.
Frame 56 data.data: 4448435043 (ASCII DHCPC).
ARP appears in frames 278, 280, 281, 282, 283, 284.
ESP packets, e.g. 157/171, illustrate additional encryption after the Wi-Fi
layer is decrypted. Do not require students to decrypt ESP or contact these IPs.

## Scope of fixture review

The file comes from the tool's published test corpus, with a documented password.
Its packet contents were inspected and its wireless decryption verified. It is
for offline parsing; this kit contains no exported payload executable. The known
password and packet answers are public facts, so require evidence and explanation
instead of grading only the password.
