"""Minimal, deterministic SKILL.md parser (no pyyaml dependency).

Parses optional YAML-ish frontmatter (simple ``key: value`` pairs) and maps
Markdown headings to canonical skill fields via a PT/EN synonym map. The
synonym map and frontmatter inference are the first line of defence against
false positives (validation.md §9 D4).
"""

from __future__ import annotations

import re

# Canonical field -> accepted heading synonyms (lowercased), PT + EN.
HEADING_SYNONYMS = {
    "purpose": [
        "purpose", "objetivo", "objective", "goal", "goals", "overview",
        "summary", "what it does", "o que faz", "descrição", "description",
    ],
    "trigger": [
        "when to use", "quando usar", "trigger", "triggers", "use when",
        "when to use this skill", "quando utilizar", "activation",
    ],
    "not_when": [
        "when not to use", "quando não usar", "quando nao usar", "do not use when",
    ],
    "inputs": [
        "inputs", "input", "inputs esperados", "expected inputs", "parameters",
        "parâmetros", "parametros", "entradas",
    ],
    "outputs": [
        "outputs", "output", "outputs esperados", "expected outputs", "result",
        "results", "returns", "saídas", "saidas", "resultado",
    ],
    "acceptance": [
        "acceptance criteria", "acceptance criterion", "critérios de aceitação",
        "criterios de aceitacao", "acceptance", "success criteria",
        "definition of done", "validation",
    ],
    # A2: "Completion Statement" is the SkillLab idiom for acceptance/definition
    # of done. Kept as its own field so `tests` stays independent.
    "completion": [
        "completion statement", "completion statement format", "completion criteria",
    ],
    "examples": [
        "examples", "exemplos", "example", "usage", "exemplos de uso",
        "usage examples", "example usage", "uso",
    ],
    # A3: many skills express boundaries as Red Flags / Counter-Examples /
    # Non-goals / Out of Scope rather than "Limitations".
    "limitations": [
        "limitations", "limitações", "limitacoes", "limits", "constraints",
        "known limitations", "restrições", "restricoes",
        "non-goals", "non goals", "out of scope", "red flags", "risk flags",
        "counter-examples", "counter examples", "failure modes",
    ],
    "tests": [
        "test cases", "tests", "testes", "casos de teste", "test", "test case",
        "test requirements",
    ],
}

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.MULTILINE)


def parse_frontmatter(text: str):
    """Return (frontmatter_dict, body_without_frontmatter)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    block = match.group(1)
    body = text[match.end():]
    fm = {}
    for line in block.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            fm[key] = value
    return fm, body


def _canonical_for_heading(heading_text: str):
    norm = heading_text.strip().lower()
    for field_name, synonyms in HEADING_SYNONYMS.items():
        for syn in synonyms:
            if norm == syn or norm.startswith(syn + " ") or norm.startswith(syn + ":"):
                return field_name
    return None


def extract_sections(body: str):
    """Map canonical field -> section content (str). Absent fields omitted."""
    sections = {}
    headings = list(_HEADING_RE.finditer(body))
    title = None
    for i, m in enumerate(headings):
        level = len(m.group(1))
        text = m.group(2).strip()
        start = m.end()
        # A1: a section runs until the next heading of the SAME or HIGHER level
        # (a sibling or ancestor). Deeper sub-headings (e.g. "### Example 1"
        # under "## Examples") belong to it, so their content is not lost.
        end = len(body)
        for nxt in headings[i + 1:]:
            if len(nxt.group(1)) <= level:
                end = nxt.start()
                break
        content = body[start:end].strip()
        if level == 1 and title is None:
            title = text
        field_name = _canonical_for_heading(text)
        if field_name is not None and field_name not in sections:
            sections[field_name] = content
    return title, sections


def parse_skill_text(skill_id: str, text: str, path=None):
    """Parse raw SKILL.md text into a Skill (imported lazily to avoid cycle)."""
    from .models import Skill

    frontmatter, body = parse_frontmatter(text)
    title, sections = extract_sections(body)

    fields = dict(sections)

    # Infer purpose from frontmatter description when no explicit purpose section.
    desc = str(frontmatter.get("description", "") or "").strip()
    if "purpose" not in fields and desc:
        fields["purpose"] = desc

    # Infer a trigger when the description states a usage condition.
    if "trigger" not in fields and desc:
        low = desc.lower()
        if any(tok in low for tok in ("use when", "when ", "quando", "usar", "use this")):
            fields["trigger"] = desc

    title = title or frontmatter.get("name") or skill_id

    return Skill(
        id=skill_id,
        path=path,
        title=title,
        frontmatter=frontmatter,
        fields=fields,
        body=body,
        raw=text,
        exists=True,
    )
