"""Discover and parse SKILL.md files under a directory.

Deterministic: skills are returned sorted by id.
"""

from __future__ import annotations

from pathlib import Path

from .models import Skill
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

    A skill is identified by the name of the directory containing its
    SKILL.md. Directories under root that contain no SKILL.md but look like
    skill folders are reported as MISSING_SKILL_FILE via an empty Skill.
    """
    root = Path(root)
    skills = []
    seen_dirs = set()

    for path in find_skill_files(root):
        skill_dir = path.parent
        seen_dirs.add(skill_dir.resolve())
        skill_id = skill_dir.name if skill_dir != root else (root.name or "root")
        text = path.read_text(encoding="utf-8")
        skills.append(parse_skill_text(skill_id, text, path=path))

    # Detect immediate child directories that declare themselves as skills
    # (they exist) but contain no SKILL.md at all.
    if root.is_dir():
        for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
            if not child.is_dir():
                continue
            if child.resolve() in seen_dirs:
                continue
            has_skill_md = any(
                p.name.lower() == "skill.md" for p in child.rglob("*") if p.is_file()
            )
            if not has_skill_md:
                skills.append(
                    Skill(id=child.name, path=child, title=child.name, exists=False)
                )

    return sorted(skills, key=lambda s: s.id.lower())
