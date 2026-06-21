"""Clarity rules: ambiguity, verbosity, missing tests."""

from __future__ import annotations

import re

from ..findings import FindingCode, Severity
from ..models import Finding

# Ambiguity markers (PT + EN). Counted against the body.
AMBIGUOUS_TERMS = [
    "maybe", "somehow", "probably", "perhaps", "as needed", "appropriate",
    "etc", "and so on", "things", "stuff", "some kind of", "or something",
    "talvez", "de alguma forma", "provavelmente", "se possível", "se possivel",
    "conforme necessário", "conforme necessario", "coisas", "algo assim",
]

# Verbosity threshold (characters of body). Above this -> INFO.
VERBOSE_CHAR_LIMIT = 6000

# A4: ambiguity is measured by DENSITY (vague terms per 1,000 words), not an
# absolute count, so long but precise skills are not penalised for a few stray
# vague words. A small absolute-count guard avoids misfiring on tiny documents.
# Calibration evidence (SkillLab corpus): a false positive sat at ~3 terms /
# 1,000 words; a genuinely vague skill at ~200 / 1,000 words.
AMBIGUITY_MIN_HITS = 3            # ignore docs with only a stray vague term or two
AMBIGUITY_WARN_DENSITY = 10.0     # per 1,000 words -> MAJOR
AMBIGUITY_BLOCK_DENSITY = 25.0    # per 1,000 words (with >=6 hits) -> blocking

_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _count_ambiguous(text):
    low = text.lower()
    count = 0
    for term in AMBIGUOUS_TERMS:
        count += len(re.findall(r"\b" + re.escape(term) + r"\b", low))
    return count


def check(skill):
    findings = []
    body = skill.body or ""

    ambiguous_hits = _count_ambiguous(body)
    words = len(_WORD_RE.findall(body))
    density = ambiguous_hits / max(words, 1) * 1000
    if ambiguous_hits >= AMBIGUITY_MIN_HITS and density >= AMBIGUITY_WARN_DENSITY:
        blocking = density >= AMBIGUITY_BLOCK_DENSITY and ambiguous_hits >= 6
        findings.append(Finding(
            code=FindingCode.AMBIGUOUS_LANGUAGE,
            severity=Severity.MAJOR,
            message=(
                f"Excessive ambiguity ({ambiguous_hits} vague terms in {words} words, "
                f"{density:.0f}/1000). "
                "Replace vague language with concrete, executable instructions."
                + (" Skill is too ambiguous to execute reliably." if blocking else "")
            ),
            skill=skill.id,
            blocking=blocking,
        ))

    if len(body) > VERBOSE_CHAR_LIMIT:
        findings.append(Finding(
            code=FindingCode.OVERLY_VERBOSE,
            severity=Severity.INFO,
            message=f"Skill is very long ({len(body)} chars). Consider tightening.",
            skill=skill.id,
        ))

    if not skill.has_field("tests"):
        findings.append(Finding(
            code=FindingCode.NO_TEST_CASES,
            severity=Severity.MINOR,
            message="No test cases documented.",
            skill=skill.id,
        ))

    return findings
