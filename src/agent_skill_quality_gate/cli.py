"""skillgate CLI.

Exit codes:
  0  gate passed (or --advisory)
  1  gate failed (blocking finding or average < --fail-under)
  2  tool / input error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .report import render_json, render_markdown, render_terminal
from .rules import evaluate
from .scanner import scan_skills
from .scoring import build_report

EXIT_OK = 0
EXIT_GATE_FAILED = 1
EXIT_ERROR = 2


def run_scan(path, fail_under=60, advisory=False):
    """Core entry used by both the CLI and tests. Returns a ScanReport."""
    root = Path(path)
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")
    skills = scan_skills(root)
    findings_by_skill = evaluate(skills)
    return build_report(skills, findings_by_skill, fail_under=fail_under, advisory=advisory)


def _cmd_scan(args):
    try:
        report = run_scan(args.path, fail_under=args.fail_under, advisory=args.advisory)
    except (NotADirectoryError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR

    if not report.results:
        print("error: no skills found (looked for SKILL.md files).", file=sys.stderr)
        return EXIT_ERROR

    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(report), encoding="utf-8")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_json(report), encoding="utf-8")

    if not args.quiet:
        print(render_terminal(report))
        if args.report:
            print(f"\nMarkdown report: {args.report}")
        if args.json:
            print(f"JSON report: {args.json}")

    return EXIT_OK if report.gate_passed else EXIT_GATE_FAILED


def build_parser():
    parser = argparse.ArgumentParser(
        prog="skillgate",
        description="Quality gate for AI agent skills (validates SKILL.md files).",
    )
    parser.add_argument("--version", action="version", version=f"skillgate {__version__}")
    sub = parser.add_subparsers(dest="command")

    scan = sub.add_parser("scan", help="Scan a folder of skills and score them.")
    scan.add_argument("path", help="Directory containing skill folders with SKILL.md files.")
    scan.add_argument("--report", metavar="PATH", help="Write the Markdown report to PATH.")
    scan.add_argument("--json", metavar="PATH", help="Write the minimal CI JSON report to PATH.")
    scan.add_argument(
        "--fail-under", type=int, default=60, metavar="N",
        help="Fail the gate if the average score is below N (default: 60).",
    )
    scan.add_argument(
        "--advisory", action="store_true",
        help="Report only — never set a failing exit code (for calibration).",
    )
    scan.add_argument("--quiet", action="store_true", help="Suppress the terminal summary.")
    scan.set_defaults(func=_cmd_scan)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return EXIT_ERROR
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
