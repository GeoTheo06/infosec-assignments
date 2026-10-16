#!/usr/bin/env python3
"""Browser grader for the imitation-page lab.

Visits the published tracked URL, submits a FRESH random dummy username/password
(never a real or a classmate's credential), and confirms the matching
"Submitted Data" event reaches the correct group's collector via the management
API. Runs with no teacher/admin browser session — only the group's own tracked
URL plus a read of the management API to verify.

    python grade.py --config ../publish/config.json --publish-result result.json
    python grade.py --selftest     # offline: exercises the timeline parser only

The automatic grade is functional (does a fresh dummy submission reach the right
collector for the deployed page version?). Visual resemblance and the written
explanation are reviewed manually.
"""
from __future__ import annotations

import argparse
import json
import secrets
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "publish"))


def fresh_marker() -> tuple[str, str]:
    return (f"dummy-{secrets.token_hex(5)}", f"pw-{secrets.token_hex(6)}")


def find_submission_event(campaign: dict, rid: str, username: str) -> dict | None:
    """Pure: does the campaign timeline contain a Submitted-Data event for this
    recipient (rid) carrying our exact dummy username? Returns the event or None."""
    results = campaign.get("results") or []
    email = next((r.get("email") for r in results if r.get("id") == rid), None)
    for ev in campaign.get("timeline") or []:
        if ev.get("message") != "Submitted Data":
            continue
        # Match by rid if present on the event, else by the recipient email.
        details = ev.get("details")
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except json.JSONDecodeError:
                details = {}
        payload = (details or {}).get("payload", {})
        got_users = payload.get("username", [])
        got_rid = payload.get("rid", [])
        rid_ok = (rid in got_rid) or (email is not None and ev.get("email") == email)
        if rid_ok and username in got_users:
            return ev
    return None


def run_live(config_path: str, publish_result_path: str, *, attempts: int = 10,
             delay: float = 1.0) -> dict:
    import requests
    from gophish_client import GoPhishClient

    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    pub = json.loads(Path(publish_result_path).read_text(encoding="utf-8"))
    rid = pub["result_id"]
    tracked = pub["tracked_url"]
    username, password = fresh_marker()

    verify = cfg.get("verify_tls", True)
    sess = requests.Session()
    sess.verify = verify
    # 1. Visit the tracked URL (records the click), then 2. submit the form.
    sess.get(tracked, timeout=15)
    sess.post(tracked, data={"username": username, "password": password,
                             "rid": rid}, timeout=15)

    # 3. Confirm via the management API.
    client = GoPhishClient(cfg["base_url"], cfg["api_key"], verify_tls=verify)
    found = None
    for _ in range(attempts):
        campaign = client.get_campaign(pub["campaign_id"])
        found = find_submission_event(campaign, rid, username)
        if found:
            break
        time.sleep(delay)

    return {
        "ok": found is not None,
        "group_name": pub.get("group_name"),
        "campaign_id": pub["campaign_id"],
        "result_id": rid,
        "submitted_username": username,
        "event_found": bool(found),
    }


def selftest() -> int:
    """Offline check of the timeline parser with a synthetic GoPhish payload."""
    rid = "abc123"
    username = "dummy-deadbeef"
    campaign = {
        "results": [{"id": rid, "email": "r1@lab.example"}],
        "timeline": [
            {"email": "r1@lab.example", "message": "Clicked Link"},
            {"email": "r1@lab.example", "message": "Submitted Data",
             "details": json.dumps({"payload": {
                 "username": [username], "password": ["pw-x"], "rid": [rid]}})},
        ],
    }
    assert find_submission_event(campaign, rid, username) is not None
    assert find_submission_event(campaign, rid, "someone-else") is None
    # wrong recipient / no submission
    empty = {"results": [{"id": rid, "email": "r1@lab.example"}], "timeline": []}
    assert find_submission_event(empty, rid, username) is None
    print("selftest OK: timeline parser matches only the exact fresh marker.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Imitation-page browser grader")
    ap.add_argument("--config")
    ap.add_argument("--publish-result")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not (args.config and args.publish_result):
        print("ERROR: --config and --publish-result required (or --selftest)",
              file=sys.stderr)
        return 2
    report = run_live(args.config, args.publish_result)
    print(f"imitation grader — {'PASS' if report['ok'] else 'FAIL'}")
    print(f"  group={report['group_name']} campaign={report['campaign_id']}")
    print(f"  submitted fresh marker {report['submitted_username']!r}; "
          f"event found: {report['event_found']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
