# Transactional Create Note

status: completed

## Problem

`createNote` appended directly and ignored `save()` failure, unlike the app's
transactional insertion path. A failed archive write could therefore leave an
unsaved note in memory.

## Design

Delegate convenience creation to `persistNewNote` and preserve the existing
returned note reference for source compatibility. The shared insertion boundary
normalizes content, enforces the note limit, and removes failed notes from memory.
This keeps failed notes out of memory after an archive write error.

## Verification

- The baseline failed before implementation on the direct append/save path.
- Focused XCTest verifies writer failure returns the same note reference while
  store count remains zero and identity lookup returns nil.
- All four Make gates passed from the checkout and `/tmp` through the absolute Makefile path.
- Two hostile mutations restoring direct append/save or removing identity evidence were rejected.
- Python syntax, shell syntax, and `git diff --check` passed.
- Local Xcode is unavailable; hosted macOS XCTest remains authoritative.

## Scope Boundaries

- The UI already uses `persistNewNote`; no visible flow, archive format,
  normalization, file protection, deletion, editing, sync, export, or logging changed.
