from conftest import GOOD_SKILL, write_skill

from agent_skill_quality_gate.findings import (
    FindingCode,
    Severity,
    Verdict,
    verdict_for,
)
from agent_skill_quality_gate.models import Finding
from agent_skill_quality_gate.rules import evaluate
from agent_skill_quality_gate.scanner import scan_skills
from agent_skill_quality_gate.scoring import build_report, score_findings


def f(severity, blocking=False, impact=None):
    return Finding(
        code=FindingCode.UNCLEAR_TRIGGER,
        severity=severity,
        message="x",
        skill="s",
        blocking=blocking,
        score_impact=impact,
    )


def test_severity_weights():
    assert score_findings([f(Severity.CRITICAL)]) == 80
    assert score_findings([f(Severity.MAJOR)]) == 90
    assert score_findings([f(Severity.MINOR)]) == 97
    assert score_findings([f(Severity.INFO)]) == 99


def test_score_clamped_at_zero():
    assert score_findings([f(Severity.CRITICAL)] * 10) == 0


def test_derived_marker_does_not_penalize():
    assert score_findings([f(Severity.INFO, impact=0)]) == 100


def test_verdict_bands():
    assert verdict_for(95) == Verdict.EXCELLENT
    assert verdict_for(85) == Verdict.PASS
    assert verdict_for(75) == Verdict.ADVISORY
    assert verdict_for(55) == Verdict.WEAK
    assert verdict_for(40) == Verdict.FAIL


def test_good_skill_scores_excellent(tmp_path):
    write_skill(tmp_path, "demo", GOOD_SKILL)
    report = build_report(scan_skills(tmp_path), evaluate(scan_skills(tmp_path)))
    result = report.results[0]
    assert result.score == 100
    assert result.verdict == Verdict.EXCELLENT


def test_blocking_finding_fails_gate_even_with_high_score(tmp_path):
    # A skill that is complete (high score) but contains an unsafe instruction.
    text = GOOD_SKILL + "\n## Danger\n```\nrm -rf /\n```\n"
    write_skill(tmp_path, "danger", text)
    skills = scan_skills(tmp_path)
    report = build_report(skills, evaluate(skills), fail_under=0)
    assert report.blocked is True
    assert report.gate_passed is False


def test_advisory_never_fails_gate(tmp_path):
    write_skill(tmp_path, "bare", "# bare\n## Steps\nx\n")  # blocking findings
    skills = scan_skills(tmp_path)
    report = build_report(skills, evaluate(skills), advisory=True)
    assert report.gate_passed is True


def test_fail_under_threshold(tmp_path):
    write_skill(tmp_path, "demo", GOOD_SKILL)
    skills = scan_skills(tmp_path)
    report = build_report(skills, evaluate(skills), fail_under=101)
    assert report.gate_passed is False
