# Note Delete Result Guard

status: completed

## Context

`NoteStore.deleteNote(index:)` already ignored invalid indexes, but callers could
not tell whether a note was actually removed. The table view should delete a
visible row only after the store reports a successful local delete.

## Completed Scope

- Changed `deleteNote(index:)` to return `false` for invalid indexes and `true`
  after a saved removal.
- Updated table-row deletion to depend on the store delete result.
- Added unit coverage for invalid delete indexes leaving the local note list
  unchanged.
- Extended the static baseline and docs so delete result handling remains tied
  to local-only note persistence.

## Verification

- `make check`
- `git diff --check`
