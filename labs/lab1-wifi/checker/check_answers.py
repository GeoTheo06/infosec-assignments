#!/usr/bin/env python3
"""Lab 1 (Wi-Fi) automated answer checker.

Validates a student's JSON answer sheet against the TA answer key. The key is
bound to the pinned capture by SHA-256: if the supplied capture does not match,
the checker refuses to grade (answers must correspond to the official fixture).

Design points from the brief:
  * Accepts *alternative* complete handshake sets, not one hard-coded sequence.
  * Requires correct packet evidence alongside the password; the publicly
    documented password alone does not pass.
  * Pure standard library (no third-party deps) so it runs on any course image.

Usage:
    python check_answers.py --key answer_key.json \
        --capture wpa2-psk-linksys.cap student_answers.json

Exit code 0 = pass, 1 = fail, 2 = usage/precondition error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _norm_mac(value: str) -> str:
    """Normalize a MAC to lowercase colon form; return '' if not a MAC."""
    hexonly = re.sub(r"[^0-9a-fA-F]", "", str(value))
    if len(hexonly) != 12:
        return ""
    return ":".join(hexonly[i : i + 2] for i in range(0, 12, 2)).lower()


def _norm_hex(value: str) -> str:
    s = str(value).strip().lower()
    if s.startswith("0x"):
        s = s[2:]
    s = re.sub(r"[\s:]", "", s)
    return s


def _as_int(value) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def grade(answers: dict, key: dict) -> dict:
    results: list[dict] = []
    earned = 0.0
    possible = 0.0
    field_pass: dict[str, bool] = {}

    for name, spec in key["fields"].items():
        weight = float(spec.get("weight", 1))
        possible += weight
        ok = False
        detail = ""

        kind = spec["type"]
        if kind in ("exact", "exact_ci"):
            got = answers.get(name)
            exp = spec["value"]
            if kind == "exact_ci":
                ok = str(got).strip().lower() == str(exp).strip().lower()
            else:
                ok = str(got).strip() == str(exp)
            detail = f"got={got!r} expected={exp!r}"
        elif kind == "enum_ci":
            got = str(answers.get(name, "")).strip().lower()
            ok = got in [v.lower() for v in spec["values"]]
            detail = f"got={got!r} allowed={spec['values']}"
        elif kind == "mac":
            ok = _norm_mac(answers.get(name, "")) == _norm_mac(spec["value"])
            detail = f"got={answers.get(name)!r} expected={spec['value']!r}"
        elif kind == "ip":
            ok = str(answers.get(name, "")).strip() == spec["value"]
            detail = f"got={answers.get(name)!r} expected={spec['value']!r}"
        elif kind == "hex":
            ok = _norm_hex(answers.get(name, "")) == _norm_hex(spec["value"])
            detail = f"got={answers.get(name)!r} expected={spec['value']!r} (ascii {spec.get('ascii')})"
        elif kind == "one_of_sets":
            got = answers.get(name)
            got_set = None
            if isinstance(got, list):
                ints = [_as_int(x) for x in got]
                if all(i is not None for i in ints):
                    got_set = frozenset(ints)
            accepted = [frozenset(s) for s in spec["sets"]]
            ok = got_set in accepted
            detail = f"got={got!r} accepted_sets={spec['sets']}"
        elif kind == "one_of_pairs":
            req = _as_int(answers.get(spec["request_field"]))
            rep = _as_int(answers.get(spec["reply_field"]))
            ok = [req, rep] in [list(p) for p in spec["pairs"]]
            detail = (
                f"request={answers.get(spec['request_field'])!r} "
                f"reply={answers.get(spec['reply_field'])!r} "
                f"accepted_pairs={spec['pairs']}"
            )
        else:
            detail = f"unknown field type {kind!r}"

        field_pass[name] = ok
        if ok:
            earned += weight
        results.append(
            {"field": name, "ok": ok, "weight": weight, "detail": detail,
             "note": spec.get("note", "")}
        )

    missing_required = [
        f for f in key.get("required_for_pass", []) if not field_pass.get(f, False)
    ]
    fraction = earned / possible if possible else 0.0
    passed = (not missing_required) and fraction >= key.get(
        "pass_threshold_fraction", 0.8
    )
    return {
        "passed": passed,
        "score_fraction": round(fraction, 4),
        "earned": earned,
        "possible": possible,
        "missing_required": missing_required,
        "fields": results,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Lab 1 Wi-Fi answer checker")
    ap.add_argument("answers", help="student answers JSON file")
    ap.add_argument("--key", required=True, help="TA answer key JSON")
    ap.add_argument(
        "--capture",
        help="path to the capture the student analyzed; its sha256 must match the key",
    )
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON only")
    args = ap.parse_args(argv)

    key = json.loads(Path(args.key).read_text(encoding="utf-8"))

    if args.capture:
        cap = Path(args.capture)
        if not cap.exists():
            print(f"ERROR: capture not found: {cap}", file=sys.stderr)
            return 2
        digest = _sha256(cap)
        if digest != key["capture"]["sha256"]:
            print(
                "ERROR: capture SHA-256 does not match the pinned fixture.\n"
                f"  got      {digest}\n  expected {key['capture']['sha256']}\n"
                "Refusing to grade: answers must be derived from the official file.",
                file=sys.stderr,
            )
            return 2
    else:
        print(
            "WARNING: no --capture supplied; grading answers without binding to the "
            "pinned fixture hash.",
            file=sys.stderr,
        )

    answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    report = grade(answers, key)

    if args.json:
        print(json.dumps(report, indent=2))
        return 0 if report["passed"] else 1

    print(f"Lab 1 Wi-Fi checker — {'PASS' if report['passed'] else 'FAIL'}")
    print(f"  score: {report['earned']:.0f}/{report['possible']:.0f} "
          f"({report['score_fraction'] * 100:.0f}%)")
    for r in report["fields"]:
        mark = "OK " if r["ok"] else "XX "
        print(f"  [{mark}] {r['field']:<28} {r['detail']}")
    if report["missing_required"]:
        print("  missing required evidence: " + ", ".join(report["missing_required"]))
    mr = key.get("manual_review")
    if mr:
        print(f"  (manual) {mr['field']}: needs TA review — not auto-scored")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
