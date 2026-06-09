# Note Title Normalization Plan

status: completed

## Context

The detail controller trims blank note titles and falls back to `Untitled` before
saving. That behavior should live in a small model helper so it can be covered by
unit assertions and reused without duplicating UI controller logic.

## Objectives

- Move note-title trimming and blank-title fallback into `Note`.
- Keep detail saves using the shared helper.
- Replace generated unit-test placeholders with focused title-normalization
  assertions.
- Extend the static baseline so app-code testability and title normalization
  stay visible on hosts without Xcode.
- Keep note content local and avoid adding sync, upload, or logging behavior.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
