"""Rule engine: run all rules over a set of skills.

13 distinct checks across structure (7), safety (2), clarity (3) and
duplication (1), plus the derived MISSING_SKILL_FILE and PUBLICATION_NOT_READY
markers.
"""

from __future__ import annotations

from ..findings import FindingCode, Severity
from ..models import Finding
from . import clarity, duplication, publication, safety, structure

PER_SKILL_RULES = (structure.check, safety.check, clarity.check)


def evaluate(skills):
    """Return dict: skill_id -> list[Finding] (deterministically ordered)."""
    from ..findings import SEVERITY_ORDER

    findings_by_skill = {s.id: [] for s in skills}

    for skill in skills:
        if not skill.exists:
            findings_by_skill[skill.id].append(Finding(
                code=FindingCode.MISSING_SKILL_FILE,
                severity=Severity.CRITICAL,
                message="No SKILL.md found in this skill directory.",
                skill=skill.id,
                blocking=True,
            ))
            continue
        for rule in PER_SKILL_RULES:
            findings_by_skill[skill.id].extend(rule(skill))

    for finding in duplication.check(skills):
        findings_by_skill[finding.skill].append(finding)

    for skill in skills:
        derived = publication.derive(skill, findings_by_skill[skill.id])
        findings_by_skill[skill.id].extend(derived)

    # Deterministic ordering: severity, then code, then message.
    for skill_id, items in findings_by_skill.items():
        items.sort(key=lambda f: (SEVERITY_ORDER[f.severity], f.code.value, f.message))

    return findings_by_skill
