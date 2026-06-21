"""Structural rules: presence/quality of the expected SKILL.md fields."""

from __future__ import annotations

from ..findings import FindingCode, Severity
from ..models import Finding


def check(skill):
    findings = []

    if not skill.has_field("purpose"):
        findings.append(Finding(
            code=FindingCode.MISSING_PURPOSE,
            severity=Severity.CRITICAL,
            message="Skill has no clear purpose/objective. Add a Purpose section or a frontmatter description.",
            skill=skill.id,
            blocking=True,
        ))

    if not skill.has_field("trigger"):
        findings.append(Finding(
            code=FindingCode.UNCLEAR_TRIGGER,
            severity=Severity.MAJOR,
            message="No clear trigger. State when the skill should be used (e.g. a 'When to use' section).",
            skill=skill.id,
        ))

    if not skill.has_field("inputs"):
        findings.append(Finding(
            code=FindingCode.MISSING_INPUTS,
            severity=Severity.MAJOR,
            message="Expected inputs are not declared.",
            skill=skill.id,
        ))

    if not skill.has_field("outputs"):
        findings.append(Finding(
            code=FindingCode.MISSING_OUTPUTS,
            severity=Severity.CRITICAL,
            message="Expected outputs are not declared (total absence of expected output).",
            skill=skill.id,
            blocking=True,
        ))

    # A2: acceptance is satisfied by explicit acceptance criteria, a completion
    # statement, OR documented test cases (any one is enough as validation
    # evidence). `tests` stays a separate field so NO_TEST_CASES is independent.
    if not (skill.has_field("acceptance") or skill.has_field("completion") or skill.has_field("tests")):
        findings.append(Finding(
            code=FindingCode.MISSING_ACCEPTANCE_CRITERIA,
            severity=Severity.MAJOR,
            message="No acceptance criteria / completion statement / test cases.",
            skill=skill.id,
        ))

    if not skill.has_field("examples"):
        findings.append(Finding(
            code=FindingCode.MISSING_EXAMPLES,
            severity=Severity.MINOR,
            message="No usage examples.",
            skill=skill.id,
        ))

    if not skill.has_field("limitations"):
        findings.append(Finding(
            code=FindingCode.NO_LIMITATIONS,
            severity=Severity.MINOR,
            message="No limitations documented.",
            skill=skill.id,
        ))

    return findings
