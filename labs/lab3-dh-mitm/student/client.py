"""Student client + helpers for the DH MITM lab.

`LabClient` talks to the running service over HTTP (use it in a notebook). The
attack function you write receives an `api` object with the same four methods,
so the grader can run your exact function against a fresh in-process instance.

Helpers re-exported for convenience (you do NOT implement DH arithmetic or AES
from scratch):
    P, G, Q            fixed group parameters
    is_valid_public    subgroup/validity check
    modexp             == pow(base, exp, mod)
    derive_key, encrypt, decrypt   the documented key/AEAD helpers
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from dhlab.crypto import decrypt, derive_key, encrypt  # noqa: E402,F401
from dhlab.params import G, P, Q, is_valid_public        # noqa: E402,F401

modexp = pow  # modexp(base, exp, mod)


class LabClient:
    """HTTP client implementing the `api` contract used by attack functions."""

    def __init__(self, base_url: str = "http://127.0.0.1:5006", timeout: float = 10.0):
        self.base = base_url.rstrip("/")
        self.timeout = timeout
        self.s = requests.Session()

    def _json(self, resp):
        if resp.status_code >= 400:
            try:
                msg = resp.json().get("error", resp.text)
            except Exception:
                msg = resp.text
            raise RuntimeError(f"HTTP {resp.status_code}: {msg}")
        return resp.json()

    def params(self) -> dict:
        return self._json(self.s.get(f"{self.base}/params", timeout=self.timeout))

    def create_session(self) -> dict:
        return self._json(self.s.post(f"{self.base}/sessions", timeout=self.timeout))

    def substitute(self, session_id: str, to_alice: int, to_bob: int) -> dict:
        return self._json(self.s.post(
            f"{self.base}/sessions/{session_id}/substitute",
            json={"to_alice": str(to_alice), "to_bob": str(to_bob)},
            timeout=self.timeout,
        ))

    def deliver(self, session_id: str, packet: dict) -> dict:
        return self._json(self.s.post(
            f"{self.base}/sessions/{session_id}/deliver",
            json=packet, timeout=self.timeout,
        ))

    def transcript(self, session_id: str) -> dict:
        return self._json(self.s.get(
            f"{self.base}/sessions/{session_id}/transcript", timeout=self.timeout))
