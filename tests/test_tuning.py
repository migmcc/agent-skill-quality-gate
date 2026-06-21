"""Tests for the calibration tuning run (A1-A4).

A1 — sections with content only in sub-headings are not treated as empty.
A2 — acceptance satisfied by Completion Statement OR Test Cases.
A3 — limitations satisfied by Red Flags / Counter-Examples / Non-goals / Out of Scope.
A4 — ambiguity is density-based, not absolute count.
"""

from conftest import GOOD_SKILL, write_skill

from agent_skill_quality_gate.findings import FindingCode
from agent_skill_quality_gate.rules import evaluate
from agent_skill_quality_gate.scanner import scan_skills


def codes_for(tmp_path, skill_id):
    skills = scan_skills(tmp_path)
    fbs = evaluate(skills)
    return {f.code for f in fbs[skill_id]}


# --- A1 -------------------------------------------------------------------

def test_a1_section_content_in_subheadings_is_present(tmp_path):
    text = (
        "---\nname: s\ndescription: Use when demonstrating subheading parsing.\n---\n"
        "# s\n## Purpose\nDo a thing.\n## When to use\nUse when X.\n"
        "## Inputs\n- a\n## Outputs\n- b\n## Test cases\n- TC-1\n"
        "## Examples\n\n### Example 1\nA concrete example body.\n### Example 2\nAnother one.\n"
    )
    write_skill(tmp_path, "s", text)
    skill = {s.id: s for s in scan_skills(tmp_path)}["s"]
    assert skill.has_field("examples")
    assert FindingCode.MISSING_EXAMPLES not in codes_for(tmp_path, "s")


# --- A2 -------------------------------------------------------------------

def _skill_without_acceptance_heading(extra_section):
    return (
        "---\nname: s\ndescription: Use when validating acceptance synonyms.\n---\n"
        "# s\n## Objective\nDo a thing well.\n## When to use\nUse when X.\n"
        "## Inputs\n- a\n## Outputs\n- b\n## Limitations\n- one case\n"
        + extra_section
    )


def test_a2_completion_statement_satisfies_acceptance(tmp_path):
    write_skill(tmp_path, "s", _skill_without_acceptance_heading(
        "## Completion Statement Format\n`done when X`.\n"))
    assert FindingCode.MISSING_ACCEPTANCE_CRITERIA not in codes_for(tmp_path, "s")


def test_a2_test_cases_satisfy_acceptance(tmp_path):
    write_skill(tmp_path, "s", _skill_without_acceptance_heading(
        "## Test Cases\n- TC-1: input X -> output Y.\n"))
    codes = codes_for(tmp_path, "s")
    assert FindingCode.MISSING_ACCEPTANCE_CRITERIA not in codes
    assert FindingCode.NO_TEST_CASES not in codes  # tests stays independent


def test_a2_still_flags_when_no_acceptance_evidence(tmp_path):
    # No acceptance, no completion, no tests -> still flagged (no over-suppression).
    write_skill(tmp_path, "s", _skill_without_acceptance_heading("## Notes\nnothing.\n"))
    assert FindingCode.MISSING_ACCEPTANCE_CRITERIA in codes_for(tmp_path, "s")


# --- A3 -------------------------------------------------------------------

def _skill_with_boundary(heading):
    return (
        "---\nname: s\ndescription: Use when validating limitation synonyms.\n---\n"
        "# s\n## Objective\nDo a thing.\n## When to use\nUse when X.\n"
        "## Inputs\n- a\n## Outputs\n- b\n## Test cases\n- TC-1\n## Examples\nX.\n"
        f"## {heading}\n- a documented boundary.\n"
    )


def test_a3_red_flags_satisfy_limitations(tmp_path):
    write_skill(tmp_path, "s", _skill_with_boundary("Red Flags"))
    assert FindingCode.NO_LIMITATIONS not in codes_for(tmp_path, "s")


def test_a3_counter_examples_satisfy_limitations(tmp_path):
    write_skill(tmp_path, "s", _skill_with_boundary("Counter-Examples"))
    assert FindingCode.NO_LIMITATIONS not in codes_for(tmp_path, "s")


def test_a3_non_goals_and_out_of_scope_satisfy_limitations(tmp_path):
    write_skill(tmp_path, "a", _skill_with_boundary("Non-goals"))
    write_skill(tmp_path, "b", _skill_with_boundary("Out of Scope"))
    assert FindingCode.NO_LIMITATIONS not in codes_for(tmp_path, "a")
    assert FindingCode.NO_LIMITATIONS not in codes_for(tmp_path, "b")


# --- A4 -------------------------------------------------------------------

def test_a4_low_density_ambiguity_not_flagged(tmp_path):
    # ~1000 filler words with only 3 vague terms -> density ~3/1000 -> not flagged.
    filler = "alpha beta gamma delta epsilon " * 200
    text = GOOD_SKILL + "\n## Notes\n" + filler + " maybe perhaps somehow\n"
    write_skill(tmp_path, "longskill", text)
    assert FindingCode.AMBIGUOUS_LANGUAGE not in codes_for(tmp_path, "longskill")


def test_a4_high_density_ambiguity_still_flagged(tmp_path):
    text = (
        "# vague\n## Purpose\nMaybe do things and stuff, etc. Probably somehow handle "
        "whatever seems appropriate, as needed, or something. Things and stuff.\n"
        "## Outputs\nSomething.\n"
    )
    write_skill(tmp_path, "vague", text)
    assert FindingCode.AMBIGUOUS_LANGUAGE in codes_for(tmp_path, "vague")
