#!/usr/bin/env python3
"""Runnable DH MITM lab service.

    python service/server.py           # listens on http://127.0.0.1:5006

Env: DHLAB_PORT (default 5006).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_ROOT))

from dhlab.service import create_app   # noqa: E402

app = create_app()

if __name__ == "__main__":
    print("[dhlab] DH MITM service — POST /sessions to begin", file=sys.stderr)
    app.run(port=int(os.environ.get("DHLAB_PORT", "5006")))
