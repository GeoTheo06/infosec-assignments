"""STUDENT TASK — implement the recovery strategy.

`recover(rows, candidates, oracle, full_pass=False) -> {account_id: password}`

Inputs:
  rows        list of public rows: {account_id, scheme, salt, digest[, iterations]}
              `salt` is None for unsalted scheme A, a shared string for B, a
              per-row string for C/D.
  candidates  the fixed-order list of candidate passwords to try.
  oracle      a counted hasher: `oracle.digest(password, salt)` returns the hex
              digest for THIS scheme (and iterations, for D). Every call is
              counted by the trusted harness — minimise calls by hashing each
              candidate once per *distinct salt*, not once per account.
  full_pass   if True, evaluate EVERY candidate for EVERY distinct salt context
              (do not stop early). If False, you may stop hashing a salt group
              once all of its target digests are found.

Hints:
  * `from passlab.runner import group_by_salt` groups rows by salt for you.
  * Multiple accounts can share a digest (repeated passwords) — record them all.
  * Some passwords are not in `candidates`; those accounts stay unrecovered.

Grade:
    python -m grader.grade --strategy student.strategy
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from passlab.runner import group_by_salt  # noqa: E402,F401


def recover(rows, candidates, oracle, full_pass=False) -> dict:
    """TODO(student): implement salt-grouped recovery. Return {account_id: password}."""
    raise NotImplementedError("implement recover() in student/strategy.py")
