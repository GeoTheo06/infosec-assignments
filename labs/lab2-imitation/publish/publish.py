#!/usr/bin/env python3
"""Publish a student's landing HTML to GoPhish and return a tracked test URL.

Workflow (per the brief):
  1. Validate the uploaded HTML has a usable capture form (post-back, named
     username + password fields).
  2. Create/update the group's landing page via the API, with dummy-data
     capture enabled.
  3. Create a FRESH campaign (new version) each publish, so the tested page is
     exactly the version just submitted.
  4. Return the tracked recipient URL for the group's synthetic recipient.

Students do not configure SMTP or GoPhish; infra pre-creates the group, SMTP
profile (local Mailpit) and an (unused) email template. See infra/README.md.

    python publish.py --config config.json --html my_login.html
    python publish.py --html my_login.html --dry-run      # validate only, no API
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from gophish_client import GoPhishClient, validate_landing_html


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Publish landing page to GoPhish")
    ap.add_argument("--html", required=True, help="the student's landing HTML file")
    ap.add_argument("--config", help="JSON config (see config.example.json)")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate the form only; do not contact GoPhish")
    ap.add_argument("--out", help="write the publish result JSON here")
    args = ap.parse_args(argv)

    html = Path(args.html).read_text(encoding="utf-8")
    check = validate_landing_html(html)
    print(f"form validation: {'OK' if check['ok'] else 'PROBLEMS'}")
    if check["form"]:
        print(f"  method={check['form']['method']} action={check['form']['action']!r} "
              f"inputs={check['form']['input_names']}")
    for p in check["problems"]:
        print(f"  - {p}")
    if not check["ok"]:
        print("Refusing to publish: fix the form so submissions can be captured.",
              file=sys.stderr)
        return 1
    if args.dry_run:
        print("dry-run: form is publishable; skipping GoPhish calls.")
        return 0

    if not args.config:
        print("ERROR: --config is required unless --dry-run", file=sys.stderr)
        return 2
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))

    client = GoPhishClient(cfg["base_url"], cfg["api_key"],
                           verify_tls=cfg.get("verify_tls", True))

    page_name = cfg["page_name"]
    client.upsert_page(page_name, html, redirect_url=cfg.get("redirect_url", ""))
    print(f"landing page upserted: {page_name}")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    campaign_name = f"{cfg['campaign_prefix']}-{stamp}"
    camp = client.create_campaign(
        campaign_name,
        page_name=page_name,
        template_name=cfg["template_name"],
        smtp_name=cfg["smtp_name"],
        group_name=cfg["group_name"],
        url=cfg["phish_url"],
    )
    full = client.get_campaign(camp["id"])
    results = full.get("results") or []
    if not results:
        print("ERROR: campaign has no recipient results", file=sys.stderr)
        return 3
    rid = results[0]["id"]
    tracked = client.tracked_url(cfg["phish_url"], rid)

    out = {
        "campaign_id": camp["id"],
        "campaign_name": campaign_name,
        "page_name": page_name,
        "result_id": rid,
        "tracked_url": tracked,
        "group_name": cfg["group_name"],
    }
    print("published.")
    print(f"  campaign: {campaign_name} (id {camp['id']})")
    print(f"  tracked test URL: {tracked}")
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"  wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
