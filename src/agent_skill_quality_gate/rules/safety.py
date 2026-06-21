"""Safety rules: deterministic deny-list scan for unsafe / risky instructions.

No AI. Patterns are documented and versioned here. This gate is a *floor*,
not a guarantee (see SECURITY.md).
"""

from __future__ import annotations

import re

from ..findings import FindingCode, Severity
from ..models import Finding

# Catastrophic / destructive -> UNSAFE_INSTRUCTION (CRITICAL, blocking).
UNSAFE_PATTERNS = [
    (r"\brm\s+-rf\s+/(?:\s|$)", "Destructive recursive delete of root (`rm -rf /`)."),
    (r"\brm\s+-rf\b", "Destructive recursive force delete (`rm -rf`)."),
    (r":\(\)\s*\{\s*:\s*\|\s*:&\s*\}\s*;\s*:", "Fork bomb."),
    (r"\bmkfs(\.\w+)?\b", "Filesystem format command (`mkfs`)."),
    (r"\bdd\s+if=", "Raw disk write (`dd if=`)."),
    (r">\s*/dev/sd[a-z]", "Direct write to a block device."),
    (r"curl\b[^\n|]*\|\s*(sudo\s+)?(sh|bash)\b", "Pipe-to-shell of remote content (`curl | sh`)."),
    (r"wget\b[^\n|]*\|\s*(sudo\s+)?(sh|bash)\b", "Pipe-to-shell of remote content (`wget | bash`)."),
]

# Risky but not necessarily catastrophic -> SHELL_RISK (MAJOR, non-blocking).
SHELL_RISK_PATTERNS = [
    (r"\bchmod\s+-R?\s*777\b", "Overly permissive permissions (`chmod 777`)."),
    (r"\bsudo\b", "Unscoped privilege escalation (`sudo`)."),
    (r"--no-verify\b", "Bypasses git hooks (`--no-verify`)."),
    (r"git\s+push\s+.*--force\b", "Force push."),
    (r"--force\b", "Force flag used."),
    (r"verify\s*=\s*False", "TLS/SSL verification disabled."),
    (r"\beval\s*\(", "Dynamic code execution (`eval(`)."),
]

def _scan_targets(skill):
    """Return the text scanned for unsafe patterns.

    The scan is intentionally **whole-file**: the entire raw `SKILL.md`
    (frontmatter + prose + code blocks + inline code) is matched against the
    deny-list. This is the conservative choice — a dangerous command is flagged
    wherever it appears, not only inside fenced code. As documented in
    SECURITY.md, this check is a floor, not a guarantee.
    """
    return skill.raw or skill.body or ""


def check(skill):
    findings = []
    text = _scan_targets(skill)

    seen = set()
    for pattern, message in UNSAFE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if message in seen:
                continue
            seen.add(message)
            findings.append(Finding(
                code=FindingCode.UNSAFE_INSTRUCTION,
                severity=Severity.CRITICAL,
                message=f"Unsafe instruction: {message}",
                skill=skill.id,
                blocking=True,
            ))

    for pattern, message in SHELL_RISK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if message in seen:
                continue
            seen.add(message)
            findings.append(Finding(
                code=FindingCode.SHELL_RISK,
                severity=Severity.MAJOR,
                message=f"Shell risk: {message}",
                skill=skill.id,
            ))

    return findings
