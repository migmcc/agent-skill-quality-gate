"""Discover and parse SKILL.md files under a directory.

Deterministic: skills are returned sorted by id.
"""

from __future__ import annotations

from pathlib import Path

from .parser import parse_skill_text


def find_skill_files(root: Path):
    """Return sorted list of SKILL.md paths under root (case-insensitive)."""
    matches = [
        p for p in root.rglob("*")
        if p.is_file() and p.name.lower() == "skill.md"
    ]
    return sorted(matches, key=lambda p: str(p).lower())


def scan_skills(root: Path):
    """Parse all skills under root.

    Only directories that contain a SKILL.md are treated as skills. A plain
    directory is not enough evidence that a skill was intended; it may hold
    auxiliary scripts, references, or assets.
    """
    root = Path(root)
    skills = []

    for path in find_skill_files(root):
        skill_dir = path.parent
        if skill_dir == root:
            skill_id = root.name or "root"
        else:
            skill_id = skill_dir.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        skills.append(parse_skill_text(skill_id, text, path=path))

    return sorted(skills, key=lambda s: s.id.lower())
