# Note Archive Path Guard Plan

status: completed

## Context

`NoteStore` writes local notes to `NoteStore.plist` in the app documents directory. If that directory lookup fails, writing to a bare fallback path can put note content somewhere outside the intended app documents archive.

## Objectives

- Make `archiveFilePath()` return nil when the documents path is unavailable.
- Skip archive saves when no documents path exists.
- Load an empty note list when no documents path exists.
- Extend the static baseline so fallback archive writes do not return.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
