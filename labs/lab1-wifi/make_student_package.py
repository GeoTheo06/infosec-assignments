#!/usr/bin/env python3
"""Build the lab 1 student package (zip), excluding all TA-only material.

Student package contains ONLY:
  wpa2-psk-linksys.cap, rockyou-first-10000.txt, the two license notices,
  HANDOUT.md, answers.template.json, and the checker (which reads a key at
  grade time but ships no answers).

TA-only (never included): ta/answer_key.json, ta/reference_answers.json,
ta/negative_answers.json, ta/TA-README.md, ta/verification.json.

Usage:  python make_student_package.py [-o out.zip]
"""
from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDENT_FILES = [
    "student/wpa2-psk-linksys.cap",
    "student/rockyou-first-10000.txt",
    "student/AIRCRACK-NG-LICENSE.txt",
    "student/SECLISTS-LICENSE.txt",
    "student/HANDOUT.md",
    "student/answers.template.json",
    "checker/check_answers.py",
]
FORBIDDEN_SUBSTRINGS = ("answer_key", "reference_answers", "negative_answers",
                        "TA-README", "verification.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=str(HERE / "lab1-wifi-student.zip"))
    args = ap.parse_args()

    out = Path(args.out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in STUDENT_FILES:
            src = HERE / rel
            if not src.exists():
                raise SystemExit(f"missing expected student file: {src}")
            arc = Path("lab1-wifi") / Path(rel).name
            # safety: never let a TA artifact slip in
            if any(bad in arc.name for bad in FORBIDDEN_SUBSTRINGS):
                raise SystemExit(f"refusing to package TA artifact: {arc}")
            zf.write(src, str(arc))

    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    names = zipfile.ZipFile(out).namelist()
    print(f"wrote {out}  ({out.stat().st_size} bytes)")
    print(f"sha256 {digest}")
    print("contents:")
    for n in names:
        print(f"  {n}")
    # final guard
    leaked = [n for n in names if any(b in n for b in FORBIDDEN_SUBSTRINGS)]
    if leaked:
        raise SystemExit(f"ERROR: TA material leaked into package: {leaked}")
    print("OK: no TA material in package.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
