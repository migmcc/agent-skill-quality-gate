"""Publication-readiness rule (derived).

PUBLICATION_NOT_READY is a non-scoring marker (score_impact=0) added when a
skill has any blocking finding. It does not double-penalize the score; it makes
the report's gate decision explicit.
"""

from __future__ import annotations

from ..findings import FindingCode, Severity
from ..models import Finding


def derive(skill, existing_findings):
    if any(f.blocking for f in existing_findings):
        blockers = sorted({f.code.value for f in existing_findings if f.blocking})
        return [Finding(
            code=FindingCode.PUBLICATION_NOT_READY,
            severity=Severity.INFO,
            message="Not ready for publication — blocking findings: " + ", ".join(blockers),
            skill=skill.id,
            blocking=True,
            score_impact=0,
        )]
    return []
