import json

from conftest import GOOD_SKILL, write_skill

from agent_skill_quality_gate.report import (
    render_json,
    render_markdown,
    render_terminal,
)
from agent_skill_quality_gate.rules import evaluate
from agent_skill_quality_gate.scanner import scan_skills
from agent_skill_quality_gate.scoring import build_report


def make_report(tmp_path):
    write_skill(tmp_path, "demo", GOOD_SKILL)
    write_skill(tmp_path, "bare", "# bare\n## Steps\nx\n")
    skills = scan_skills(tmp_path)
    return build_report(skills, evaluate(skills))


def test_markdown_has_expected_sections(tmp_path):
    md = render_markdown(make_report(tmp_path))
    assert "# Skill Quality Gate Report" in md
    assert "## Summary" in md
    assert "## Skill Results" in md
    assert "Average score:" in md


def test_json_is_valid_and_has_keys(tmp_path):
    data = json.loads(render_json(make_report(tmp_path)))
    assert data["tool"] == "agent-skill-quality-gate"
    assert data["skills_scanned"] == 2
    assert "average_score" in data
    assert "gate_passed" in data
    assert isinstance(data["results"], list)
    assert {"skill", "score", "verdict", "findings"} <= set(data["results"][0])


def test_json_is_deterministic(tmp_path):
    r1 = render_json(make_report(tmp_path))
    r2 = render_json(make_report(tmp_path))
    assert r1 == r2


def test_terminal_summary_renders(tmp_path):
    out = render_terminal(make_report(tmp_path))
    assert "Skill Quality Gate" in out
    assert "Gate:" in out
