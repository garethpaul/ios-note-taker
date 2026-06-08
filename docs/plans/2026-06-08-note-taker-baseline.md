# iOS Note Taker Baseline Plan

status: completed

## Context

`ios-note-taker` is a legacy Swift iOS note-taking sample with table/detail
controllers, keyed-archive local persistence, unit/UI test scaffolding, shared
Xcode schemes, and a shell build entry point. This Linux host does not provide
Xcode, so local verification needs a static baseline while full app builds
remain a macOS/Xcode responsibility.

## Objectives

- Persist local note changes after create, edit, and delete operations.
- Make local archive decoding tolerate missing, corrupt, or incompatible data.
- Keep note content local by default with no logging, sync, analytics, upload, or network behavior.
- Guard storyboard casts, invalid delete indexes, empty note titles, and partial invalid hex scans.
- Make `build.sh` POSIX-compatible and safe on hosts without Xcode.
- Add a reproducible `make check` baseline for project metadata, plist/storyboard/scheme XML, source inventory, and privacy guardrails.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
