from conftest import GOOD_SKILL, write_skill

from agent_skill_quality_gate.scanner import find_skill_files, scan_skills


def test_finds_all_skill_files(tmp_path):
    write_skill(tmp_path, "a", GOOD_SKILL)
    write_skill(tmp_path, "b", GOOD_SKILL)
    write_skill(tmp_path, "c", GOOD_SKILL)
    assert len(find_skill_files(tmp_path)) == 3


def test_parses_fields_and_frontmatter(tmp_path):
    write_skill(tmp_path, "demo", GOOD_SKILL)
    skills = scan_skills(tmp_path)
    assert len(skills) == 1
    skill = skills[0]
    assert skill.id == "demo"
    assert skill.frontmatter.get("name") == "demo"
    for field in ("purpose", "trigger", "inputs", "outputs", "acceptance", "examples", "limitations", "tests"):
        assert skill.has_field(field), f"expected field present: {field}"


def test_auxiliary_directories_are_not_treated_as_missing_skills(tmp_path):
    skill_dir = write_skill(tmp_path, "my-skill", GOOD_SKILL)
    for name in ("scripts", "references", "assets"):
        (skill_dir / name).mkdir()

    skills = scan_skills(skill_dir)

    assert [skill.id for skill in skills] == ["my-skill"]


def test_unrelated_collection_directories_are_not_treated_as_skills(tmp_path):
    write_skill(tmp_path, "real", GOOD_SKILL)
    for name in ("docs", "custom-support"):
        (tmp_path / name).mkdir()

    skills = scan_skills(tmp_path)

    assert [skill.id for skill in skills] == ["real"]


def test_nested_skills_use_unique_relative_path_ids(tmp_path):
    write_skill(tmp_path, "team-a/repo-audit", GOOD_SKILL)
    write_skill(tmp_path, "team-b/repo-audit", GOOD_SKILL)

    ids = [skill.id for skill in scan_skills(tmp_path)]

    assert ids == ["team-a/repo-audit", "team-b/repo-audit"]


def test_scan_is_deterministic(tmp_path):
    write_skill(tmp_path, "b", GOOD_SKILL)
    write_skill(tmp_path, "a", GOOD_SKILL)
    ids = [s.id for s in scan_skills(tmp_path)]
    assert ids == sorted(ids)
