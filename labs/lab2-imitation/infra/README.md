# Lab 2 infrastructure — GoPhish + Mailpit

Prepared serving/collection stack. Students never touch this; a TA runs one
isolated instance per group and hands students a tracked URL and the publish
config.

## Bring up a per-group instance

GoPhish publishes no official image, so the stack **builds GoPhish from the
official source** pinned to release `v0.12.1`; Mailpit is a pinned published
image. The first `up` builds GoPhish (needs network + git; a few minutes). To
build it once up front:

```bash
docker compose -p lab2-group-01 build gophish
```

Then start the per-group instance (pick distinct ports per group on a shared host):

```bash
GROUP=group-01 ADMIN_PORT=3333 PHISH_PORT=8080 MAILPIT_UI=8025 docker compose -p lab2-group-01 up -d
```

- Admin UI/API: `https://127.0.0.1:3333` (self-signed; keep private to TA/group).
- Published landing origin: `http://127.0.0.1:8080` (where students submit).
- Mailpit inbox: `http://127.0.0.1:8025` (no mail is sent in the assessed task).

The management origin (3333) is deliberately separate from the published page
origin (8080), as the brief requires.

## First login + API key

On first start GoPhish prints a random admin password in the container log:

```bash
docker compose -p lab2-group-01 logs gophish | grep -i "please login"
```

Log in at the admin UI, set a password, then copy the **API key** from
*Settings*. Use it for provisioning and publishing.

## Provision the group objects

```bash
python provision.py --base-url https://127.0.0.1:3333 --api-key <KEY> \
    --group group-01 --no-verify-tls
```

This creates the SMTP profile (`mailpit-local` → `mailpit:1025`), a no-op
template, and a group with one synthetic recipient. It prints the names to put
in `publish/config.json`.

## Configuration & state

- GoPhish runs with its **built-in config**: admin on `:3333` (self-signed TLS,
  auto-generated on first run), phishing server on `:80` (remapped to the host
  `PHISH_PORT`). We deliberately do **not** mount a custom `config.json` or a
  named DB volume — the container runs as a non-root user and overriding the DB
  path onto a root-owned volume makes GoPhish fail to start (crash loop).
- State is therefore **per-container**: recreating the container is a clean
  reset. That is fine here — each publish already creates a fresh
  campaign/version, so the graded page is always the one just submitted.
- `gophish/config.json` in this folder is an **optional reference/override**. If
  you need persistence or custom ports, mount it **writable** (not `:ro`, since
  GoPhish's entrypoint may rewrite it) and point `db_path` at a location the
  container's `app` user can write (e.g. the default `gophish.db`), not a
  root-owned mount.

## Isolation & hygiene

- One compose project per group → isolated network and container, no cross-group
  data.
- Keep the admin port bound to localhost or a TA-only network.
- All mail/submissions are course test traffic with dummy markers; students
  never collect a real or a classmate's credential.

## Images (pinned)

| Service | Source |
|---------|--------|
| GoPhish | built from `github.com/gophish/gophish` at tag **v0.12.1** (its in-tree Dockerfile) → tagged `infosec-lab/gophish:v0.12.1` |
| Mailpit | `axllent/mailpit:v1.31.6` (published image) |

GoPhish has no official Docker Hub image, so we build the pinned release from
source rather than depend on a third-party image. If your host can't reach
GitHub at build time, build the image once on a connected host and push it to
your own registry, keeping the `v0.12.1` tag.

## Reset a group

```bash
docker compose -p lab2-group-01 down        # removes the container -> clean slate
GROUP=group-01 docker compose -p lab2-group-01 up -d
python provision.py ... --group group-01    # re-provision
```

State is per-container, so `down` (recreate) is the full reset. Each publish
also creates a fresh campaign/version, so per-submission resets aren't needed.
