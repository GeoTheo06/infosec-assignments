# Lab 2 — A login page that lies

Here's a login page. It has a logo, the right colours, a padlock, a "secure
sign-in" badge, a copyright footer. Half of those things are telling you the
truth and half are pure theatre — and the page has no way of proving which. Your
job: rebuild it convincingly, publish it to your lab address, and then tell me
exactly two things the page can't hide if you look — **where it really lives**
and **where your password really goes.**

This is the uncomfortable corner of the SSL lecture made personal. Remember the
slide where Eve sends her own certificate — one that *shows "Bob"* but isn't
signed by a CA, or one that's signed but *isn't Bob* — and the lecturer asked
"what happens then?" The answer on the slide was blunt: **"Nothing happens"**,
and the note underneath said the real flaw "isn't in the SSL protocol… it's a
flaw in human nature." This lab is you, standing on the human-nature side of that
flaw, building the thing that exploits it — so you'll never fall for it again.

> Ground rules: the organisation is fictional ("Aurelia Polytechnic"), every
> credential is a disposable dummy, and your page only ever lives inside your
> isolated lab instance. You never collect a real or a classmate's password.
> This is a lab about *identity and trust*, run safely.

## Where this sits in the course

- **Website identity = a certificate** (Protocols/SSL): the lecture called an
  SSL certificate "an ID card that proves someone is who they say they are",
  holding the site's public key. A convincing *look* is not an ID card. You'll
  point at what the actual identity signal is versus what's just paint.
- **The human-nature flaw** (Protocols): "nothing happens" when the cert is
  wrong but the page looks right. That gap between *looks trustworthy* and *is
  verified* is the entire exercise.
- **Impersonation & fake identity** (GPG fake-public-key, Access Control
  "impersonation"): same shape as the fake-key attack — attacker presents an
  identity the victim doesn't verify. Here the "identity" is a whole web page.
- **Sender identity you can forge** (Hashing lecture): email spoofing is trivial
  because "MTAs don't verify who you claim to be" — SPF/DKIM/DMARC exist to bolt
  identity back on. A look-alike login page is the web version of a spoofed
  From: address.

## What you're given

- A **reference page** to study and reproduce: `reference-portal/index.html` plus
  `reference-portal/assets/` (the logo). Open it; notice *which* details make it
  feel legitimate.
- A **form starter**, `student-starter/login.html`, whose `<form>` already posts
  back correctly and names its fields — restyle freely around it.
- From your TA: a **tracked URL** for your group and a **publish config**.

## Workflow

1. **Inspect** the reference. List the trust cues (logo, colours, the padlock and
   "secure" badge, labels, footer). Which of these could *anyone* copy in five
   minutes? (That's the point — all of them.)
2. **Rebuild** it (an editor, an AI coding tool, or by editing the starter). Keep
   the form working:
   - `method="post"` and an **empty** `action` (so it posts back to the page);
   - both inputs keep a `name` (`username`, `password`);
   - link only to the supplied assets.
3. **Check** the form before publishing:
   ```bash
   python publish/publish.py --html your_login.html --dry-run
   ```
4. **Publish** to your lab address:
   ```bash
   python publish/publish.py --config publish/config.json --html your_login.html --out result.json
   ```
   This prints your **tracked test URL** and writes `result.json`.
5. **Submit a dummy marker** via that tracked URL (not the editor preview): open
   it, type any dummy ID and password, submit.
6. **Check the collector**: your submission shows up in your group's results —
   confirm your dummy values arrived.

## The two questions that are the whole point

In your write-up, answer these — they're the parts a pretty page can't fake:

1. **Where does the page really live?** Look at the actual origin (host/port in
   the address bar), not the logo. If this were real, how would the SSL
   certificate — the lecture's "ID card" — give the lie away? What would you
   check?
2. **Where does your password really go?** Trace the form submission. The visual
   says "Aurelia Polytechnic"; where does the POST actually land? Tie this back
   to the spoofed-sender idea: the visible identity and the real destination are
   two different things, and only one of them is verified.

Also pick **two visual trust cues** you reproduced and say, honestly, how much
skill each took to fake. (It's sobering how little.)

## Grading

- **Automatic (functional):** the page loads, the form works, and a fresh dummy
  submission reaches your group's collector for the version you just published. A
  bot submitting successfully proves the *plumbing* works — it says nothing about
  whether a human would be fooled, which is why the next part is by hand.
- **By hand (small):** the visual resemblance and your answers about origin,
  destination and trust cues. A gorgeous copy with a broken form fails the
  functional check; a working but generic form earns no resemblance credit.

## What you need

A browser and (optionally) an editor or AI tool. You do **not** set up any
servers — the infrastructure, URL and assets are provided. Go make something
convincing, then come back able to explain precisely why "it looked right"
should never have been enough.
