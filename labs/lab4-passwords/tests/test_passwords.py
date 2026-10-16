"""Lab 4 acceptance tests (main benchmark + reuse + bonus)."""
import pytest

from bonus import reference as bonus_ref
from bonus.rainbow import Counter, build_full_lookup_table, covered_passwords, hash_hex, P
from passlab import schemes
from passlab.candidates import CANDIDATES, CANDIDATE_COUNT
from passlab.generator import make_d_release, make_release
from passlab.hashcat_export import export
from passlab.reuse import run_reuse_experiment
from passlab.runner import run
from ta.reference_strategy import recover as ref_recover


# --- schemes / encoding ------------------------------------------------------

def test_candidate_list_fixed_and_distinct():
    assert len(CANDIDATES) == CANDIDATE_COUNT == 512
    assert len(set(CANDIDATES)) == 512


def test_salt_is_hashed_as_ascii_not_hexdecoded():
    # Scheme B hashes the displayed hex characters, not the decoded bytes.
    salt = "ab" * 16  # 32 hex chars
    expected = schemes.hashlib.sha256(b"pw" + salt.encode("ascii")).hexdigest()
    assert schemes.compute("B", "pw", salt) == expected


# --- controlled full-pass evaluation counts (the headline numbers) -----------

@pytest.mark.parametrize("scheme,expected", [("A", 512), ("B", 512), ("C", 6144)])
def test_fullpass_counts_match_brief(scheme, expected):
    fx = make_release(1234, scheme)
    report = run(fx, ref_recover, full_pass=True)
    assert report["evaluations"] == expected
    assert report["distinct_salts"] * report["candidates"] == expected


def test_recovery_mode_not_more_work_than_fullpass():
    for scheme in ("A", "B", "C"):
        fx = make_release(1234, scheme)
        full = run(fx, ref_recover, full_pass=True)
        rec = run(fx, ref_recover, full_pass=False)
        assert rec["evaluations"] <= full["evaluations"]


def test_in_list_recovered_out_of_list_not():
    fx = make_release(1234, "C")
    report = run(fx, ref_recover, full_pass=True)
    assert report["recovered_correct"] == report["recoverable_in_list"]
    assert report["recovered_wrong"] == 0
    # there ARE out-of-list accounts that stay unrecovered
    assert report["recoverable_in_list"] < report["accounts"]


def test_equivalent_inputs_across_schemes():
    # A, B, C share the account/password assignment (same passwords recovered).
    a = run(make_release(7, "A"), ref_recover, full_pass=True)["correct"]
    b = run(make_release(7, "B"), ref_recover, full_pass=True)["correct"]
    c = run(make_release(7, "C"), ref_recover, full_pass=True)["correct"]
    assert a == b == c


# --- scheme D ---------------------------------------------------------------

def test_scheme_d_recovers_with_pbkdf2():
    fx = make_d_release(7, iterations=1000)
    report = run(fx, ref_recover, full_pass=True)
    assert report["evaluations"] == 2 * 128  # 2 distinct salts * 128 candidates
    assert report["recovered_correct"] == report["recoverable_in_list"]


# --- reuse experiment --------------------------------------------------------

def test_reuse_only_when_salt_matches():
    r = run_reuse_experiment(seed=1)
    v = r["variants"]
    assert v["same_shared_salt"]["reusable"] is True
    assert v["changed_shared_salt"]["reusable"] is False
    assert v["no_salt"]["reusable"] is False
    assert v["new_individual_salts"]["reusable"] is False
    # changing the salt forces recomputation; individual salts multiply it
    assert r["recompute_cost_changed_shared_salt"] == 512
    assert r["recompute_cost_individual_salts"] == r["individual_salt_distinct_contexts"] * 512
    # an unsalted table DOES reuse across unsalted releases
    assert r["unsalted_table_reuses_across_unsalted_releases"] > 0


# --- hashcat export sanity ---------------------------------------------------

def test_hashcat_modes_and_shapes():
    assert export(make_release(1, "A"))["mode"] == 1400
    b = export(make_release(1, "B"))
    assert b["mode"] == 1410 and ":" in b["lines"][0]
    d = export(make_d_release(1, 1000))
    assert d["mode"] == 10900 and d["lines"][0].startswith("sha256:1000:")


# --- bonus: rainbow table ----------------------------------------------------

def test_bonus_reference_recovers_covered_and_is_smaller():
    starts = P[:128]
    L = 8
    counter = Counter()
    table = bonus_ref.build_rainbow_table(starts, L, counter)
    stored = sum(len(v) for v in table.values())
    assert stored < len(build_full_lookup_table())      # smaller than full lookup
    covered = covered_passwords(starts, L)
    sample = list(covered)[:15]
    hits = 0
    for pw in sample:
        got = bonus_ref.rainbow_lookup(hash_hex(pw), table, L)
        if got is not None and hash_hex(got) == hash_hex(pw):
            hits += 1
    assert hits == len(sample)   # all covered targets recovered & verified


def test_bonus_no_false_positive_for_salted_target():
    starts = P[:128]
    L = 8
    table = bonus_ref.build_rainbow_table(starts, L)
    salted = hash_hex("alpha000" + "deadbeef" * 4)
    got = bonus_ref.rainbow_lookup(salted, table, L)
    assert got is None or hash_hex(got) == salted   # never an unverified hit


def test_student_strategy_stub_not_implemented():
    import student.strategy as s
    with pytest.raises(NotImplementedError):
        s.recover([], [], None)
