# Lab 2 — Imitation login page

Students reproduce a **fictional** reference portal, publish it to an isolated
per-group GoPhish landing page, and demonstrate a dummy submission reaching the
collector. GoPhish serves and captures; we supply the reference page, the
publish workflow and a browser grader. A full email campaign is out of scope.

> Controlled training exercise only: a fictional organization, disposable dummy
> credentials, isolated per-group instances, and course test traffic. No real
> brand is imitated and no real credentials are ever collected.

## Layout

```
lab2-imitation/
├─ reference-portal/        fictional "Aurelia Polytechnic" portal (students reproduce)
│  ├─ index.html            inline CSS, links only to assets/
│  └─ assets/logo.svg
├─ student-starter/login.html   working POST form starter (named fields, empty action)
├─ publish/
│  ├─ gophish_client.py     REST client + offline landing-form validator
│  ├─ publish.py            upload HTML, enable capture, create fresh campaign, return tracked URL
│  └─ config.example.json
├─ grader/grade.py          submit fresh dummy marker, verify event via management API (+ --selftest)
├─ infra/
│  ├─ docker-compose.yml    GoPhish built from source @v0.12.1 + Mailpit v1.31.6, per-group
│  ├─ gophish/config.json
│  ├─ provision.py          create group/SMTP/template for an instance
│  └─ README.md
├─ tests/test_imitation.py  offline: form validation + event-parser (8 tests)
├─ conftest.py
├─ student-handout.md
└─ README.md
```

## What runs where

- **Offline / here:** form validation (`validate_landing_html`), publish
  `--dry-run`, grader `--selftest`, and the whole test suite:
  ```bash
  pytest tests -q                                   # 8 tests
  python publish/publish.py --html reference-portal/index.html --dry-run
  python grader/grade.py --selftest
  ```
- **Needs the stack (TA, per group):** `infra/` compose + `provision.py`, then
  `publish.py --config ...` and the live `grade.py --config ... --publish-result ...`.

## Design notes mapped to the brief

| Brief point | Implementation |
|---|---|
| Fictional reference portal: logo, colors, labels, working-looking form; simple, no build system | `reference-portal/` (inline CSS, one asset link). |
| GoPhish serving/capture, isolated per group; management separate from page origin | `infra/docker-compose.yml` (per-project; admin :3333 vs phish :8080). |
| One synthetic recipient per group + local SMTP (Mailpit); initializes tracked URLs; no email sent | `infra/provision.py` (group + `mailpit-local` SMTP + no-op template). |
| Minimal publish: accept one HTML file, create/update landing page, enable capture, return tracked URL; fresh campaign/version each publish | `publish/publish.py` + `gophish_client.upsert_page` / `create_campaign`. |
| Form starter: POST, empty action, named username+password, capture enabled | `student-starter/login.html`; capture flags set on upsert. |
| Browser grader: visit tracked URL, submit fresh random dummy values, confirm via management API; no admin session | `grader/grade.py` (fresh marker, `find_submission_event`). |
| Functional auto-grade vs manual visual/explanation; broken form fails functionality | handout grading section; validator rejects broken/exfiltrating forms. |
| Students don't configure SMTP/GoPhish/DNS | all infra TA-side; students get URL + assets + publish script. |

## Reset procedure

Per submission: not needed — each publish makes a fresh campaign/version, so the
graded page is exactly the one just submitted. Full group reset:

```bash
docker compose -p lab2-group-01 down -v && \
GROUP=group-01 docker compose -p lab2-group-01 up -d && \
python infra/provision.py --base-url https://127.0.0.1:3333 --api-key <KEY> --group group-01 --no-verify-tls
```

## Shipping to students

Ship `reference-portal/`, `student-starter/`, `publish/` and `student-handout.md`.
Keep `infra/` and the admin API key TA-side. The grader runs TA-side against the
management API.

## Optional: driving the submission from the course browser

`grader/grade.py` submits with `requests`. A Selenium/Playwright variant can
drive a real browser to the tracked URL and submit the form; the verification
step (reading the management API for the exact fresh marker) is identical. The
API confirmation is what establishes the event reached the collector, so the
`requests` version is sufficient to grade.
