# Note File Protection Plan

status: completed

## Context

`ios-note-taker` persists notes locally in `NoteStore.plist`. Notes can contain sensitive personal information, so successful archive writes should also apply platform file protection to the local archive.

## Objectives

- Preserve the existing local `NSKeyedArchiver` save path.
- Apply `NSFileProtectionComplete` after a successful archive write.
- Avoid logging note content or local file paths when file protection cannot be set.
- Extend the static baseline so local archive file protection remains visible.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
