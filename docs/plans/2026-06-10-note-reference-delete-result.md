# Note Reference Delete Result

status: completed

## Context

`NoteStore.deleteNote(index:)` reports whether a delete actually removed and
saved a note, but `deleteNote(withNote:)` silently returned `Void`. Any future
caller deleting by object reference would not be able to distinguish a
successful removal from a missing or already-deleted note.

## Completed Scope

- Changed reference-based note deletion to return `Bool`.
- Returned `true` only after removing the matching note and saving the archive.
- Returned `false` when the note reference is not present in the store.
- Added focused XCTest assertions for successful reference deletion and repeated
  deletion failure.
- Extended the static baseline and docs so reference delete results remain
  visible without adding sync, upload, analytics, or network behavior.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
