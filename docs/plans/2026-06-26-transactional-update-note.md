# Transactional Legacy Note Update

status: completed

## Problem

The legacy `updateNote(theNote:)` API normalizes a stored note and reports
archive write failure, but leaves the mutated fields in memory. Create, detail
editing, and delete paths already roll back failed persistence, so this public
store path violates the same saved-state invariant.

## Design

- Track title/text snapshots only after successful load or save.
- On `updateNote` failure, restore the target note from its last successful
  snapshot.
- Keep object identity, date, archive format, normalization, and the newer
  `persistChanges` API unchanged.

## Test First

Inject a writer that succeeds for initial creation and fails for a later legacy
update. Require `updateNote` to return false and restore the original title and
text on the same note object.

## Verification

- Focused XCTest red then hosted green
- Portable static and hostile contracts
- All Make aliases and external-Makefile gate
- `git diff --check`

## Scope Boundaries

- No archive schema, sync, export, networking, logging, or UI changes.
- Direct arbitrary `save()` callers remain responsible for their own mutations;
  this change repairs the explicit legacy update API.

The implementation records each note's last successful snapshot after load or
save and restores that content when the legacy update write fails. Portable and
hosted verification includes hostile mutations that remove snapshot lookup,
title rollback, text rollback, and snapshot refresh evidence.
All four Python 3.9 Make aliases and the external-Makefile gate passed, along
with Python compilation and `git diff --check`. Local `xcodebuild` is
unavailable, so hosted macOS remains authoritative for Swift and XCTest. Push
Check run `28267525297`, pull-request Check run `28267527105` attempt 2, and
CodeQL run `28267526088` passed on implementation head
`3fd508c195eb7cf910eeecf4c3087e7a95a77804`. Codex review stopped before
analysis with OpenAI HTTP 401; immutable manual review found no actionable
issues. The evidence-only final head must repeat hosted validation before merge.
