# Hosted Project Validation

status: completed

## Context

The static baseline covered note privacy, persistence guardrails, schemes, and
project metadata, but it only printed a reminder when Xcode was installed. The
repository also relied on a legacy Travis declaration with no current hosted
project-file check.

## Completed Scope

- Added a pinned GitHub Actions workflow with read-only repository permissions.
- Runs the canonical `make check` gate on a bounded `macos-15` job.
- Parses `NoteTaker.xcodeproj` and its shared schemes whenever Xcode is
  available.
- Kept note archives, local note content, simulator builds, and signing outside
  hosted CI.
- Extended the checker and documentation to preserve the CI contract.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- workflow YAML parse
- `git diff --check`
