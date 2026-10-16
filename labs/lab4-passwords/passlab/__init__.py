"""passlab — shared library for Lab 4 (password-breach benchmark).

Modules:
    schemes      the four storage schemes A/B/C/D and the counted hash oracle.
    candidates   the fixed-order candidate list (with a few absent passwords).
    generator    seeded fixture generator + private answer manifest.
    runner       instrumented recovery runner (recovery vs controlled full-pass).
    reuse        cross-release / cross-salt reuse experiment.
    benchmark    monotonic timing harness for the slow-KDF comparison.
    hashcat_export  export A/B/C/D to Hashcat modes 1400/1410/10900.
    grader       validate recovered accounts + rerun strategies on fresh fixtures.

Encoding (unambiguous, per the brief):
    * candidate passwords are ASCII;
    * salts are 32-char ASCII hex strings from 16 random bytes, and those
      DISPLAYED ASCII characters are hashed directly (not hex-decoded);
    * digests are stored as hex; parameters are stored alongside.
"""
