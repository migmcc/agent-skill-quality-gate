---
name: open-source-readiness
description: Use when auditing a public repository for open-source readiness before publishing it.
---

# open-source-readiness

## Purpose

Audit a public repository for open-source readiness, checking license, README,
contributing guide and security policy before the repository is published.

## When to use

Use when preparing a repository to go public and you need to confirm it meets
open-source readiness standards.

## Inputs

- A path to the repository to audit.

## Outputs

- A readiness checklist with pass/fail per item.

## Acceptance criteria

- Every readiness item is reported with a pass/fail status.

## Examples

Audit `./my-repo` and return the readiness checklist.

## Limitations

- Does not fix issues; it only reports them.

## Test cases

- TC-1: a repo missing a README fails the readme item.
