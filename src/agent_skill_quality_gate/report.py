"""Report renderers: Markdown, minimal JSON (CI), and a terminal summary."""

from __future__ import annotations

import json

from .findings import SEVERITY_ORDER


def render_markdown(report):
    lines = []
    lines.append("# Skill Quality Gate Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"Skills scanned: {len(report.results)}")
    lines.append(f"Average score: {report.average_score}/100")
    lines.append(f"Verdict: {report.global_verdict.value.upper()}")
    gate = "PASS" if report.gate_passed else "FAIL"
    if report.advisory:
        gate += " (advisory — exit 0)"
    lines.append(f"Gate: {gate}")
    lines.append("")

    if report.top_issues:
        lines.append("## Top Issues")
        lines.append("")
        for i, issue in enumerate(report.top_issues, 1):
            lines.append(f"{i}. {issue}")
        lines.append("")

    lines.append("## Skill Results")
    lines.append("")
    for r in report.results:
        lines.append(f"### {r.skill}")
        lines.append("")
        lines.append(f"Score: {r.score}/100")
        lines.append(f"Verdict: {r.verdict.value.upper()}")
        if r.blocked:
            lines.append("Blocked: yes (publication blocked)")
        if r.findings:
            lines.append("")
            lines.append("Findings:")
            for f in r.findings:
                flag = " [BLOCKING]" if f.blocking else ""
                lines.append(f"- ({f.severity.value}) {f.code.value}: {f.message}{flag}")
        else:
            lines.append("")
            lines.append("No findings.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_json(report):
    """Minimal, stable JSON for CI consumption."""
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def render_terminal(report):
    """Plain-text terminal summary (brief §8 shape)."""
    lines = []
    lines.append("Skill Quality Gate")
    lines.append("")
    lines.append(f"Skills scanned: {len(report.results)}")
    lines.append(f"Average score: {report.average_score}/100")
    lines.append(f"Verdict: {report.global_verdict.value.upper()}")

    critical = []
    for r in report.results:
        for f in r.findings:
            if f.blocking:
                critical.append(f"- {r.skill}: {f.code.value}")
    if critical:
        lines.append("")
        lines.append("Critical issues:")
        # stable + de-duplicated
        for item in sorted(set(critical)):
            lines.append(item)

    gate = "PASS" if report.gate_passed else "FAIL"
    if report.advisory:
        gate += " (advisory)"
    lines.append("")
    lines.append(f"Gate: {gate}")
    return "\n".join(lines)
