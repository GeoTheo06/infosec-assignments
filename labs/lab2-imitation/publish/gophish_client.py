"""Minimal GoPhish REST client + landing-page form validation.

Used by the publish workflow and the grader. The HTML/form validation needs no
network and is unit-tested; the REST calls follow the documented GoPhish API:
  landing pages: https://docs.getgophish.com/api-documentation/landing-pages
  campaigns:     https://docs.getgophish.com/api-documentation/campaigns
"""
from __future__ import annotations

import re
from html.parser import HTMLParser


# --------------------------------------------------------------------------- #
# Offline: validate a student's landing HTML has a usable capture form.
# --------------------------------------------------------------------------- #
class _FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict] = []
        self._in_form = False
        self._cur: dict | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self._in_form = True
            self._cur = {"method": (a.get("method") or "").lower(),
                         "action": a.get("action"), "inputs": []}
        elif tag == "input" and self._in_form and self._cur is not None:
            self._cur["inputs"].append({
                "name": a.get("name"), "type": (a.get("type") or "text").lower(),
            })

    def handle_endtag(self, tag):
        if tag == "form" and self._cur is not None:
            self.forms.append(self._cur)
            self._cur = None
            self._in_form = False


def validate_landing_html(html: str) -> dict:
    """Return {ok, problems, form}. A usable form posts back and names both a
    username-like field and a password field."""
    parser = _FormParser()
    parser.feed(html)
    problems: list[str] = []
    if not parser.forms:
        return {"ok": False, "problems": ["no <form> element found"], "form": None}

    # Prefer a form that has a password input.
    def has_pw(f):
        return any(i["type"] == "password" and i["name"] for i in f["inputs"])
    form = next((f for f in parser.forms if has_pw(f)), parser.forms[0])

    names = [i["name"] for i in form["inputs"] if i["name"]]
    pw = [i["name"] for i in form["inputs"] if i["type"] == "password" and i["name"]]
    user_like = [n for n in names
                 if re.search(r"user|email|login|id", n or "", re.I)]

    if form["method"] != "post":
        problems.append('form method should be "post"')
    if form["action"] not in (None, "", "/"):
        problems.append('form action should be empty (post back to the page), '
                        f'got {form["action"]!r}')
    if not pw:
        problems.append("no named password input (type=password with a name=)")
    if not user_like:
        problems.append("no named username/email/id input")

    return {"ok": not problems, "problems": problems,
            "form": {"method": form["method"], "action": form["action"],
                     "input_names": names, "password_fields": pw,
                     "username_fields": user_like}}


# --------------------------------------------------------------------------- #
# Online: GoPhish admin API (imported lazily so offline validation needs no deps)
# --------------------------------------------------------------------------- #
class GoPhishClient:
    def __init__(self, base_url: str, api_key: str, *, verify_tls: bool = True,
                 timeout: float = 15.0) -> None:
        import requests  # local import: offline validation doesn't need it
        self.base = base_url.rstrip("/")
        self.timeout = timeout
        self.s = requests.Session()
        self.s.verify = verify_tls
        self.s.headers.update({"Authorization": f"Bearer {api_key}",
                               "Content-Type": "application/json"})

    def _req(self, method, path, **kw):
        resp = self.s.request(method, f"{self.base}{path}", timeout=self.timeout, **kw)
        if resp.status_code >= 400:
            raise RuntimeError(f"GoPhish {method} {path} -> {resp.status_code}: {resp.text}")
        return resp.json() if resp.content else {}

    # --- landing pages ---
    def find_page(self, name: str):
        for p in self._req("GET", "/api/pages/"):
            if p.get("name") == name:
                return p
        return None

    def upsert_page(self, name: str, html: str, *, redirect_url: str = "") -> dict:
        payload = {
            "name": name, "html": html,
            "capture_credentials": True, "capture_passwords": True,
            "redirect_url": redirect_url,
        }
        existing = self.find_page(name)
        if existing:
            payload["id"] = existing["id"]
            return self._req("PUT", f"/api/pages/{existing['id']}", json=payload)
        return self._req("POST", "/api/pages/", json=payload)

    # --- lookups for prepared infra objects ---
    def _find_named(self, path: str, name: str):
        for obj in self._req("GET", path):
            if obj.get("name") == name:
                return obj
        raise RuntimeError(f"no object named {name!r} under {path}")

    def group(self, name): return self._find_named("/api/groups/", name)
    def smtp(self, name): return self._find_named("/api/smtp/", name)
    def template(self, name): return self._find_named("/api/templates/", name)

    # --- campaigns ---
    def create_campaign(self, name, *, page_name, template_name, smtp_name,
                        group_name, url) -> dict:
        payload = {
            "name": name,
            "url": url,
            "page": {"name": page_name},
            "template": {"name": template_name},
            "smtp": {"name": smtp_name},
            "groups": [{"name": group_name}],
        }
        return self._req("POST", "/api/campaigns/", json=payload)

    def get_campaign(self, campaign_id) -> dict:
        return self._req("GET", f"/api/campaigns/{campaign_id}")

    @staticmethod
    def tracked_url(campaign_url: str, rid: str) -> str:
        return f"{campaign_url.rstrip('/')}/?rid={rid}"
