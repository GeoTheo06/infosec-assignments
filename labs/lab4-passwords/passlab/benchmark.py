"""Timing harness for the cheap-hash vs expensive-KDF comparison.

Uses a monotonic timer and repeated samples. CPU time is an *observation*, not
the primary grade — the authoritative figure is the evaluation count from the
oracle. The scheme-D run is bounded (2 accounts, 128 candidates) so it finishes
in a few minutes even at calibrated iteration counts.
"""
from __future__ import annotations

import statistics
import time

from .generator import make_d_release
from .runner import candidates_for
from .schemes import HashOracle, digest_D


def time_recovery(fixture, strategy, *, full_pass: bool, samples: int = 3) -> dict:
    cands = candidates_for(fixture)
    rows = fixture.public_rows()
    durations: list[float] = []
    evaluations = 0
    for _ in range(samples):
        oracle = HashOracle(fixture.scheme, fixture.iterations)
        t0 = time.monotonic()
        strategy(rows, cands, oracle, full_pass=full_pass)
        durations.append(time.monotonic() - t0)
        evaluations = oracle.count
    return {
        "scheme": fixture.scheme,
        "iterations": fixture.iterations,
        "candidates": len(cands),
        "distinct_salts": len({r.get("salt") for r in rows}),
        "evaluations": evaluations,
        "samples": samples,
        "seconds_min": round(min(durations), 6),
        "seconds_median": round(statistics.median(durations), 6),
    }


def compare_iterations(seed: int, iteration_counts, strategy, *,
                       samples: int = 2) -> list[dict]:
    """Run the bounded scheme-D benchmark across several iteration counts."""
    out = []
    for it in iteration_counts:
        fx = make_d_release(seed, it)
        out.append(time_recovery(fx, strategy, full_pass=True, samples=samples))
    return out


def calibrate_iterations(target_seconds: float = 0.05, start: int = 10_000,
                         cap: int = 2_000_000) -> int:
    """Find an iteration count where ONE derivation takes ~target_seconds on
    this CPU. Run before release so the whole scheme-D run stays bounded."""
    salt = "00" * 16
    iters = start
    while iters <= cap:
        t0 = time.monotonic()
        digest_D("calibrate", salt, iters)
        elapsed = time.monotonic() - t0
        if elapsed >= target_seconds:
            return iters
        # scale up proportionally toward the target (at least double)
        factor = max(2.0, target_seconds / max(elapsed, 1e-6))
        iters = int(iters * min(factor, 8))
    return cap
