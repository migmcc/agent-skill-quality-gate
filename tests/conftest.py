"""Make the src-layout package importable without an install."""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def write_skill(root, skill_id, text):
    """Helper: create <root>/<skill_id>/SKILL.md with the given text."""
    d = root / skill_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(text, encoding="utf-8")
    return d


GOOD_SKILL = """---
name: demo
description: Use when you need to demonstrate a well-formed skill for tests.
---

# demo

## Purpose
Do one clear thing well.

## When to use
Use when the test needs a complete skill.

## Inputs
- An input value.

## Outputs
- A processed result.

## Acceptance criteria
- The result matches the input transformation.

## Examples
Input X gives output Y.

## Limitations
- Handles one case only.

## Test cases
- TC-1: X -> Y.
"""
