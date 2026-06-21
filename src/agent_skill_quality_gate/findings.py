"""Finding codes, severities, weights and verdict bands.

The single source of truth for scoring constants, kept in sync with the
SkillLab planning docs (architecture.md, implementation-brief.md).
"""

from __future__ import annotations

from enum import Enum


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    INFO = "INFO"


# Score penalty per severity. Canonical tiers: CRITICAL/MAJOR/MINOR/INFO.
SEVERITY_WEIGHT = {
    Severity.CRITICAL: -20,
    Severity.MAJOR: -10,
    Severity.MINOR: -3,
    Severity.INFO: -1,
}

# Deterministic ordering for reports (most severe first).
SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.MAJOR: 1,
    Severity.MINOR: 2,
    Severity.INFO: 3,
}


class FindingCode(str, Enum):
    MISSING_SKILL_FILE = "MISSING_SKILL_FILE"
    MISSING_PURPOSE = "MISSING_PURPOSE"
    UNCLEAR_TRIGGER = "UNCLEAR_TRIGGER"
    MISSING_INPUTS = "MISSING_INPUTS"
    MISSING_OUTPUTS = "MISSING_OUTPUTS"
    MISSING_ACCEPTANCE_CRITERIA = "MISSING_ACCEPTANCE_CRITERIA"
    MISSING_EXAMPLES = "MISSING_EXAMPLES"
    OVERLY_VERBOSE = "OVERLY_VERBOSE"
    UNSAFE_INSTRUCTION = "UNSAFE_INSTRUCTION"
    SHELL_RISK = "SHELL_RISK"
    DUPLICATE_SCOPE = "DUPLICATE_SCOPE"
    AMBIGUOUS_LANGUAGE = "AMBIGUOUS_LANGUAGE"
    NO_LIMITATIONS = "NO_LIMITATIONS"
    NO_TEST_CASES = "NO_TEST_CASES"
    PUBLICATION_NOT_READY = "PUBLICATION_NOT_READY"


# Verdict bands (decision 2026-06-20: excellent/pass/advisory/weak/fail).
class Verdict(str, Enum):
    EXCELLENT = "excellent"
    PASS = "pass"
    ADVISORY = "advisory"
    WEAK = "weak"
    FAIL = "fail"


def verdict_for(score: int) -> Verdict:
    if score >= 90:
        return Verdict.EXCELLENT
    if score >= 80:
        return Verdict.PASS
    if score >= 70:
        return Verdict.ADVISORY
    if score >= 50:
        return Verdict.WEAK
    return Verdict.FAIL
