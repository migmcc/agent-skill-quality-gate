# Changelog

All notable changes to this project are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-06-21

Initial public release.

### Added
- `skillgate` CLI to scan a folder of `SKILL.md` files.
- 13 deterministic validation rules across structure, safety, clarity and duplication.
- Scoring (0–100) with severity weights (CRITICAL −20, MAJOR −10, MINOR −3, INFO −1)
  and verdict bands: excellent / pass / advisory / weak / fail.
- Blocking findings fail the gate regardless of score.
- Basic safety checks (deny-list heuristic for unsafe instructions / shell risks) —
  a floor, not a guarantee; the tool never executes scanned content.
- Markdown and minimal JSON reports + terminal summary.
- Exit codes: 0 (pass) / 1 (gate failed) / 2 (tool/input error).
- `--report`, `--json`, `--fail-under`, `--advisory`, `--quiet` flags.
- Example skills (good / weak / duplicate) and a pytest suite.
- GitHub Actions CI (Python 3.9 / 3.11 / 3.13).

### Notes
- Deterministic, no AI/LLM, no network, zero runtime dependencies (Python stdlib only).

[0.1.0]: https://github.com/migmcc/agent-skill-quality-gate/releases/tag/v0.1.0
