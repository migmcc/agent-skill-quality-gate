"""Duplication rule: deterministic, no-AI scope overlap detection.

Uses difflib.SequenceMatcher (stdlib) over normalized name+description+purpose.
rapidfuzz (planned in architecture.md) is deferred; difflib keeps v0.1
dependency-free while staying deterministic and explainable.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from ..findings import FindingCode, Severity
from ..models import Finding

DUP_WARN = 0.82   # MAJOR
DUP_BLOCK = 0.92  # CRITICAL / blocking

_WS_RE = re.compile(r"\s+")


def _signature(skill):
    parts = [
        str(skill.title or skill.id),
        skill.description,
        skill.fields.get("purpose", ""),
    ]
    text = " ".join(parts).lower()
    text = re.sub(r"[^a-z0-9áàâãéêíóôõúç ]+", " ", text)
    return _WS_RE.sub(" ", text).strip()


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def check(skills):
    """Cross-skill rule. Returns findings attributed to each side of a pair."""
    findings = []
    present = [s for s in skills if s.exists]
    sigs = {s.id: _signature(s) for s in present}

    for i in range(len(present)):
        for j in range(i + 1, len(present)):
            a, b = present[i], present[j]
            ratio = similarity(sigs[a.id], sigs[b.id])
            if ratio >= DUP_WARN:
                blocking = ratio >= DUP_BLOCK
                severity = Severity.CRITICAL if blocking else Severity.MAJOR
                pct = round(ratio * 100)
                for skill, other in ((a, b), (b, a)):
                    findings.append(Finding(
                        code=FindingCode.DUPLICATE_SCOPE,
                        severity=severity,
                        message=f"Scope overlap {pct}% with `{other.id}`.",
                        skill=skill.id,
                        blocking=blocking,
                    ))
    return findings
