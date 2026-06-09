# Note Lookup Index Guard

status: completed

## Context

`NoteStore.getNote(index:)` read directly from the backing note array. Normal
table view calls should use valid rows, but stale UI state or future callers can
ask for a negative or out-of-range index. Note lookup should reject those values
instead of crashing.

## Objectives

- Make note lookup return nil for invalid indexes.
- Keep table cell configuration behind guarded note lookup.
- Add focused unit coverage for invalid lookup indexes.
- Extend the static baseline so direct unsafe note indexing does not return.
- Preserve local-only note storage without adding sync, upload, analytics, or
  logging behavior.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
