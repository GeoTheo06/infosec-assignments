#!/usr/bin/env python3
"""Run every lab's test suite, each in its OWN pytest process.

The labs are independent packages and several reuse the same top-level package
names (`grader`, `ta`, `student`, ...). Collecting them in a single pytest
process would cross-import those names, so we run one process per lab. Each lab
on its own collects cleanly.

    python run_tests.py            # all labs with Python test suites
    python run_tests.py lab5-jwt   # just one
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LABS_WITH_TESTS = [
    "lab2-imitation",
    "lab3-dh-mitm",
    "lab4-passwords",
    "lab5-jwt",
]


def main(argv: list[str]) -> int:
    which = argv or LABS_WITH_TESTS
    failures = []
    for lab in which:
        lab_dir = ROOT / "labs" / lab
        tests = lab_dir / "tests"
        if not tests.exists():
            print(f"== {lab}: no tests/ dir, skipping ==")
            continue
        print(f"\n===================== {lab} =====================")
        rc = subprocess.call(
            [sys.executable, "-m", "pytest", "tests", "-q"], cwd=str(lab_dir)
        )
        if rc != 0:
            failures.append(lab)

    print("\n==================== summary ====================")
    if failures:
        print("FAILED: " + ", ".join(failures))
        return 1
    print("All lab test suites passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
