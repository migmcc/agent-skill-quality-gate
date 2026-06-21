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


def test_missing_skill_md_directory_is_flagged(tmp_path):
    (tmp_path / "empty-skill").mkdir()
    write_skill(tmp_path, "real", GOOD_SKILL)
    skills = scan_skills(tmp_path)
    ids = {s.id: s for s in skills}
    assert "empty-skill" in ids
    assert ids["empty-skill"].exists is False


def test_scan_is_deterministic(tmp_path):
    write_skill(tmp_path, "b", GOOD_SKILL)
    write_skill(tmp_path, "a", GOOD_SKILL)
    ids = [s.id for s in scan_skills(tmp_path)]
    assert ids == sorted(ids)
