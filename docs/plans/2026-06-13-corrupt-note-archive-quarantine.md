# Corrupt Note Archive Quarantine

status: planned

## Context

`NoteStore.load()` currently handles archive reads and secure decoding in one
`do` block. A readable but corrupt or incompatible archive therefore produces
an empty store on every launch while the same invalid bytes remain at the live
archive path. Conversely, treating every catch as corruption could move data
that is only temporarily unreadable because complete file protection is active.

## Requirements

- R1. Keep missing or unreadable protected archives in place and load an empty
  in-memory store without classifying them as corrupt.
- R2. Quarantine only archives whose bytes were read successfully but failed
  secure decoding or decoded to the wrong root type.
- R3. Move corrupt bytes to a deterministic sibling path and reapply complete
  file protection without logging note content or local paths.
- R4. Replace an older quarantine before moving the newest corrupt archive so a
  stale file cannot block recovery.
- R5. Preserve secure class-restricted decoding, atomic protected saves, and all
  existing note CRUD behavior.
- R6. Add focused XCTest intent through an injectable archive URL while keeping
  the production singleton API unchanged.

## Scope Boundaries

- Do not sync, upload, export, inspect, or log note content.
- Do not change the keyed archive format or migrate legacy unrestricted data.
- Do not change project files, schemes, storyboard routing, or workflow policy.
- Local Linux validation must remain truthful about unavailable `xcodebuild`.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile scripts/check-baseline.py`
- `sh -n build.sh`
- plist, storyboard, XIB, scheme, workspace, SVG, and workflow YAML parsing
- `git diff --check`
- Hostile mutations must reject quarantine on read failure, missing decode and
  root-type quarantine, missing replacement or protection, stale plan status,
  and missing verification evidence.
