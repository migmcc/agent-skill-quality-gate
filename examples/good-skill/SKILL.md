---
name: changelog-writer
description: Use when a release is being prepared and a human-readable changelog must be generated from merged pull requests.
---

# changelog-writer

## Purpose

Generate a clear, human-readable changelog entry for a release from a list of
merged pull requests, grouped by change type (features, fixes, docs).

## When to use

Use this skill when preparing a release and you have a list of merged PRs that
need to be summarized into release notes. Do not use it to decide version
numbers — that is the release-manager's job.

## Inputs

- A list of merged pull request titles and numbers.
- The target release version (e.g. `1.4.0`).

## Outputs

- A Markdown changelog section with the version header and grouped bullet
  points, ready to paste into `CHANGELOG.md`.

## Acceptance criteria

- Every input PR appears exactly once in the output.
- Entries are grouped under Features, Fixes and Docs headings.
- The version header matches the provided version.

## Examples

Input: PRs `#12 Add export button (feature)`, `#13 Fix crash on empty list (fix)`.
Output:

```
## 1.4.0
### Features
- Add export button (#12)
### Fixes
- Fix crash on empty list (#13)
```

## Limitations

- Does not infer change type when a PR is untagged; it asks for clarification.
- English output only in v0.1.

## Test cases

- TC-1: three PRs across all groups produce three grouped sections.
- TC-2: an untagged PR triggers a clarification request rather than a guess.
