# agent-skill-quality-gate

**Quality gate for AI agent skills.** A deterministic, local-first CLI that
validates `SKILL.md` files for clarity, structure, basic safety checks,
documented tests, duplication and publication readiness — before they are
merged or published.

- 🚫 No AI / no LLM — fully deterministic and explainable.
- 📦 Zero runtime dependencies — Python standard library only.
- 🔌 CI-friendly — fails a build on blocking findings or a low score.
- 📝 Markdown **and** JSON reports.

> ℹ️ The safety check is a deterministic deny-list heuristic — a *floor, not a
> guarantee*, and it never executes the content it scans. See [SECURITY.md](SECURITY.md).
>
> CLI command: `skillgate`. Status: **v0.1 (alpha)**.

---

## The problem

As agent projects grow, the bottleneck shifts from *writing* skills to
*trusting* them. Is a skill's purpose clear? Are its inputs/outputs defined?
Does it duplicate another skill? Does it contain an unsafe shell instruction?
Is it ready to publish? `agent-skill-quality-gate` answers these objectively.

## Quickstart (under 5 minutes)

```bash
# 1. install (editable)
pip install -e .

# 2. scan a folder of skills
skillgate scan ./examples

# 3. write reports for humans (Markdown) and CI (JSON)
skillgate scan ./examples --report reports/report.md --json reports/report.json
```

A "skill" is any directory containing a `SKILL.md` file.

### Example output

```
Skill Quality Gate

Skills scanned: 4
Average score: 65/100
Verdict: WEAK

Critical issues:
- repo-audit: DUPLICATE_SCOPE
- weak-skill: MISSING_PURPOSE
- weak-skill: UNSAFE_INSTRUCTION

Gate: FAIL
```

## What it checks (13 rules)

| Area | Findings |
|---|---|
| Structure | `MISSING_PURPOSE`, `UNCLEAR_TRIGGER`, `MISSING_INPUTS`, `MISSING_OUTPUTS`, `MISSING_ACCEPTANCE_CRITERIA`, `MISSING_EXAMPLES`, `NO_LIMITATIONS` |
| Safety | `UNSAFE_INSTRUCTION`, `SHELL_RISK` |
| Clarity | `AMBIGUOUS_LANGUAGE`, `OVERLY_VERBOSE`, `NO_TEST_CASES` |
| Duplication | `DUPLICATE_SCOPE` |
| Derived | `MISSING_SKILL_FILE`, `PUBLICATION_NOT_READY` |

## Scoring

Each skill starts at 100. Penalties by severity:

| Severity | Penalty |
|---|---|
| CRITICAL | −20 |
| MAJOR | −10 |
| MINOR | −3 |
| INFO | −1 |

Verdict bands: **excellent** ≥90 · **pass** ≥80 · **advisory** ≥70 · **weak** ≥50 · **fail** <50.

A **blocking** finding (e.g. unsafe instruction, missing purpose, missing
output, near-identical duplicate, or excessive ambiguity) fails the gate
**regardless of the numeric score**.

## CLI

```
skillgate scan <path> [--report PATH] [--json PATH] [--fail-under N] [--advisory] [--quiet]
```

| Flag | Meaning |
|---|---|
| `--report PATH` | Write the Markdown report. |
| `--json PATH` | Write the minimal CI JSON report. |
| `--fail-under N` | Fail if average score < N (default 60). |
| `--advisory` | Report only; never set a failing exit code (for calibration). |

**Exit codes:** `0` gate passed · `1` gate failed · `2` tool/input error.

### Use in CI

```yaml
- run: pip install -e .
- run: skillgate scan ./skills --fail-under 70 --json reports/gate.json
```

## Examples

- [`examples/good-skill`](examples/good-skill) — a complete, valid skill (scores 100).
- [`examples/weak-skill`](examples/weak-skill) — an invalid skill (missing purpose/outputs, unsafe `rm -rf`, ambiguous language).
- [`examples/duplicate-skills`](examples/duplicate-skills) — two skills with overlapping scope.

## Development

```bash
pip install -e ".[dev]"
pytest -q
```

## Roadmap

- **v0.1** — scan, 13 rules, scoring, Markdown + minimal JSON, exit codes. *(current)*
- **v0.2** — YAML config + custom rules, richer JSON, better duplication.
- **v0.3** — GitHub Action + PR comments + fail-on-threshold.
- **v0.4** — README badge, version comparison.
- **v0.5** — more formats (`AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `.cursor/rules`).
- **v1.0** — stable, extensible rule engine, full docs.

## Contributing

Contributions welcome. Good first issues: add a heading synonym, add a safety
deny-list pattern (with a test), or contribute an example skill. See
[`SECURITY.md`](SECURITY.md) for the safety-check scope.

## License

[MIT](LICENSE).
