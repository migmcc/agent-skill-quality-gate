# Changelog

All notable changes to this project are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-08-09

### Breaking Changes
- Skill IDs in terminal, Markdown and JSON output are now paths relative to the
  scan root, using `/` separators. For example, when scanning `./skills`,
  `./skills/team-a/repo-audit/SKILL.md` changes from `repo-audit` to
  `team-a/repo-audit`. Update stored reports, baselines and downstream
  integrations keyed by skill ID.

### Fixed
- Only directories containing a `SKILL.md` are treated as skills. Auxiliary
  directories such as `scripts/`, `references/` and `assets/` are ignored.
- Nested skills with the same directory name now keep independent findings,
  duplication signatures and report entries.

### Removed
- Removed the unreachable `MISSING_SKILL_FILE` finding and its unused skill
  existence state.

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

[0.2.0]: https://github.com/migmcc/agent-skill-quality-gate/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/migmcc/agent-skill-quality-gate/releases/tag/v0.1.0
