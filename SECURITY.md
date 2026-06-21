# Security Policy

## Scope and intent

`agent-skill-quality-gate` includes a deterministic deny-list scan that flags
**unsafe instructions** and **shell risks** inside `SKILL.md` files
(`UNSAFE_INSTRUCTION`, `SHELL_RISK`).

**This check is a floor, not a guarantee.** It uses a curated list of known
dangerous patterns (see `src/agent_skill_quality_gate/rules/safety.py`). It can
miss novel or obfuscated dangerous instructions and it does not execute or
sandbox anything. A passing gate does **not** certify a skill as safe — human
review remains required for anything that ships to production.

The tool itself:

- runs fully offline — no network calls, no telemetry;
- requires no secrets or credentials;
- never executes the content of the skills it scans.

## Reporting a vulnerability

Please report vulnerabilities **privately** via GitHub Security Advisories:
["Report a vulnerability"](https://github.com/migmcc/agent-skill-quality-gate/security/advisories/new)
(repository **Security** tab → **Report a vulnerability**).

If private advisories are unavailable, open a
[GitHub issue](https://github.com/migmcc/agent-skill-quality-gate/issues) with the
`security` label and **without** sensitive proof-of-concept details, and we will
move the discussion to a private channel.

Please do **not** disclose undisclosed vulnerabilities in public issues.

## Extending the deny-list

The unsafe-pattern list is versioned in `rules/safety.py`. Contributions that
add well-justified patterns (with a test case) are welcome.
