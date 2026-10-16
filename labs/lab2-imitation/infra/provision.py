#!/usr/bin/env python3
"""Provision a per-group GoPhish instance for the imitation-page lab.

Creates the prepared objects students never touch:
  * a group with ONE synthetic recipient (initializes tracked campaign URLs),
  * an SMTP profile pointing at the local Mailpit (students never send mail),
  * a no-op email template (required to create a campaign).

Run once per group after `docker compose up`, with that instance's admin API key
(Settings page in the GoPhish UI, or reset via the UI on first login).

    python provision.py --base-url https://127.0.0.1:3333 --api-key KEY \
        --group group-01 --no-verify-tls
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "publish"))

from gophish_client import GoPhishClient


def provision(client: GoPhishClient, group: str) -> dict:
    created = {}

    # SMTP profile -> Mailpit (internal docker hostname).
    smtp_name = "mailpit-local"
    try:
        client.smtp(smtp_name)
    except RuntimeError:
        client._req("POST", "/api/smtp/", json={
            "name": smtp_name,
            "host": "mailpit:1025",
            "from_address": "no-reply@infosec-lab.example",
            "ignore_cert_errors": True,
            "interface_type": "SMTP",
        })
    created["smtp"] = smtp_name

    # No-op email template (campaigns require one; no email is actually sent).
    tmpl_name = "noop-template"
    try:
        client.template(tmpl_name)
    except RuntimeError:
        client._req("POST", "/api/templates/", json={
            "name": tmpl_name,
            "subject": "Lab notice",
            "html": "<p>Lab environment — no action required.</p>",
            "text": "Lab environment - no action required.",
        })
    created["template"] = tmpl_name

    # Group with ONE synthetic recipient.
    group_name = f"{group}-recipients"
    try:
        client.group(group_name)
    except RuntimeError:
        client._req("POST", "/api/groups/", json={
            "name": group_name,
            "targets": [{
                "email": f"recipient@{group}.lab.example",
                "first_name": "Lab", "last_name": "Recipient",
                "position": "student",
            }],
        })
    created["group"] = group_name

    created["page_name"] = f"{group}-portal"
    return created


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Provision a GoPhish group instance")
    ap.add_argument("--base-url", default="https://127.0.0.1:3333")
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--group", required=True)
    ap.add_argument("--no-verify-tls", action="store_true")
    args = ap.parse_args(argv)

    client = GoPhishClient(args.base_url, args.api_key,
                           verify_tls=not args.no_verify_tls)
    created = provision(client, args.group)
    print("provisioned:")
    for k, v in created.items():
        print(f"  {k}: {v}")
    print("\nNow copy publish/config.example.json to config.json and set page_name,"
          f" group_name={created['group']}, smtp_name={created['smtp']},"
          f" template_name={created['template']}, and the API key.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
