"""Data models (stdlib dataclasses — no pydantic in v0.1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .findings import FindingCode, Severity, Verdict


# Canonical fields a SKILL.md is expected to declare.
CANONICAL_FIELDS = (
    "purpose",
    "trigger",
    "inputs",
    "outputs",
    "acceptance",
    "completion",
    "examples",
    "limitations",
    "tests",
)


@dataclass
class Skill:
    """A parsed SKILL.md."""

    id: str
    path: Optional[Path]
    title: Optional[str] = None
    frontmatter: dict = field(default_factory=dict)
    fields: dict = field(default_factory=dict)  # field name -> content str ("" if heading present but empty)
    body: str = ""
    raw: str = ""
    exists: bool = True

    def has_field(self, name: str) -> bool:
        """True if the field is present with non-empty content."""
        value = self.fields.get(name)
        return value is not None and value.strip() != ""

    @property
    def description(self) -> str:
        return str(self.frontmatter.get("description", "") or "")


@dataclass
class Finding:
    code: FindingCode
    severity: Severity
    message: str
    skill: str
    blocking: bool = False
    score_impact: Optional[int] = None  # None => derive from severity; 0 => no penalty

    def to_dict(self) -> dict:
        return {
            "code": self.code.value,
            "severity": self.severity.value,
            "message": self.message,
            "blocking": self.blocking,
        }


@dataclass
class SkillResult:
    skill: str
    score: int
    verdict: Verdict
    findings: list = field(default_factory=list)
    blocked: bool = False

    def to_dict(self) -> dict:
        return {
            "skill": self.skill,
            "score": self.score,
            "verdict": self.verdict.value,
            "blocked": self.blocked,
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass
class ScanReport:
    results: list = field(default_factory=list)
    average_score: int = 0
    global_verdict: Verdict = Verdict.FAIL
    top_issues: list = field(default_factory=list)
    blocked: bool = False
    gate_passed: bool = True
    fail_under: Optional[int] = None
    advisory: bool = False

    def to_dict(self) -> dict:
        return {
            "tool": "agent-skill-quality-gate",
            "version": "0.1.0",
            "skills_scanned": len(self.results),
            "average_score": self.average_score,
            "global_verdict": self.global_verdict.value,
            "blocked": self.blocked,
            "gate_passed": self.gate_passed,
            "fail_under": self.fail_under,
            "advisory": self.advisory,
            "top_issues": list(self.top_issues),
            "results": [r.to_dict() for r in self.results],
        }
