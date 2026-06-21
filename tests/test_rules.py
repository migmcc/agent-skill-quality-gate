from conftest import GOOD_SKILL, write_skill

from agent_skill_quality_gate.findings import FindingCode
from agent_skill_quality_gate.rules import evaluate
from agent_skill_quality_gate.scanner import scan_skills


def codes_for(tmp_path):
    skills = scan_skills(tmp_path)
    fbs = evaluate(skills)
    return {sid: {f.code for f in fs} for sid, fs in fbs.items()}


def test_good_skill_has_no_findings(tmp_path):
    write_skill(tmp_path, "demo", GOOD_SKILL)
    assert codes_for(tmp_path)["demo"] == set()


def test_missing_fields_flagged(tmp_path):
    write_skill(tmp_path, "bare", "# bare\n\n## Steps\nDo a thing.\n")
    codes = codes_for(tmp_path)["bare"]
    assert FindingCode.MISSING_PURPOSE in codes
    assert FindingCode.MISSING_OUTPUTS in codes
    assert FindingCode.UNCLEAR_TRIGGER in codes
    assert FindingCode.PUBLICATION_NOT_READY in codes  # derived from blocking


def test_unsafe_instruction_detected(tmp_path):
    text = GOOD_SKILL + "\n## Danger\n```\nrm -rf /\n```\n"
    write_skill(tmp_path, "danger", text)
    assert FindingCode.UNSAFE_INSTRUCTION in codes_for(tmp_path)["danger"]


def test_shell_risk_detected(tmp_path):
    text = GOOD_SKILL + "\n## Danger\n```\nsudo chmod 777 .\n```\n"
    write_skill(tmp_path, "risky", text)
    assert FindingCode.SHELL_RISK in codes_for(tmp_path)["risky"]


def test_ambiguous_language_detected(tmp_path):
    vague = (
        "# vague\n\n## Purpose\nMaybe do things and stuff, etc. "
        "Probably somehow handle whatever seems appropriate, as needed, "
        "or something. Things and stuff.\n\n## Outputs\nSomething.\n"
    )
    write_skill(tmp_path, "vague", vague)
    assert FindingCode.AMBIGUOUS_LANGUAGE in codes_for(tmp_path)["vague"]


def test_duplicate_scope_detected(tmp_path):
    write_skill(tmp_path, "alpha", GOOD_SKILL)
    write_skill(tmp_path, "beta", GOOD_SKILL)  # identical content
    codes = codes_for(tmp_path)
    assert FindingCode.DUPLICATE_SCOPE in codes["alpha"]
    assert FindingCode.DUPLICATE_SCOPE in codes["beta"]


def test_distinct_skills_not_flagged_as_duplicate(tmp_path):
    write_skill(tmp_path, "demo", GOOD_SKILL)
    other = (
        "---\nname: timer\ndescription: Use when you need to measure elapsed wall-clock time.\n---\n"
        "# timer\n## Purpose\nMeasure elapsed wall-clock time between two events.\n"
        "## When to use\nUse when timing an operation.\n## Inputs\n- start, end.\n"
        "## Outputs\n- duration in ms.\n## Acceptance criteria\n- duration is non-negative.\n"
        "## Examples\nstart=0 end=5 -> 5.\n## Limitations\n- ms resolution.\n## Test cases\n- TC-1.\n"
    )
    write_skill(tmp_path, "timer", other)
    codes = codes_for(tmp_path)
    assert FindingCode.DUPLICATE_SCOPE not in codes["demo"]
    assert FindingCode.DUPLICATE_SCOPE not in codes["timer"]


def test_missing_skill_file_flagged(tmp_path):
    (tmp_path / "ghost").mkdir()
    write_skill(tmp_path, "real", GOOD_SKILL)
    assert FindingCode.MISSING_SKILL_FILE in codes_for(tmp_path)["ghost"]
