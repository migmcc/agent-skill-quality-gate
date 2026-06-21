"""Scoring: per-skill score, verdict and the global gate decision."""

from __future__ import annotations

from .findings import SEVERITY_WEIGHT, Verdict, verdict_for
from .models import ScanReport, SkillResult


def score_findings(findings):
    """Return clamped 0..100 score from a list of findings."""
    score = 100
    for f in findings:
        impact = f.score_impact if f.score_impact is not None else SEVERITY_WEIGHT[f.severity]
        score += impact
    return max(0, min(100, score))


def build_report(skills, findings_by_skill, fail_under=60, advisory=False):
    results = []
    for skill in skills:
        findings = findings_by_skill.get(skill.id, [])
        score = score_findings(findings)
        blocked = any(f.blocking for f in findings)
        results.append(SkillResult(
            skill=skill.id,
            score=score,
            verdict=verdict_for(score),
            findings=findings,
            blocked=blocked,
        ))

    results.sort(key=lambda r: r.skill.lower())

    if results:
        average = round(sum(r.score for r in results) / len(results))
    else:
        average = 0

    any_blocked = any(r.blocked for r in results)
    below_threshold = fail_under is not None and average < fail_under
    gate_passed = advisory or not (any_blocked or below_threshold)

    top_issues = _top_issues(results)

    return ScanReport(
        results=results,
        average_score=average,
        global_verdict=verdict_for(average),
        top_issues=top_issues,
        blocked=any_blocked,
        gate_passed=gate_passed,
        fail_under=fail_under,
        advisory=advisory,
    )


def _top_issues(results, limit=5):
    counts = {}
    for r in results:
        for f in r.findings:
            counts.setdefault(f.code.value, 0)
            counts[f.code.value] += 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [f"{code} ({n} skill{'s' if n != 1 else ''})" for code, n in ranked[:limit]]
