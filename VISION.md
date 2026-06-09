## iOS Note Taker Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

iOS Note Taker is a simple Swift note-taking app with list, detail, and note
storage behavior.

The repository is useful as a compact iOS app sample with table/detail
controllers, a note model, tests, and a visual demo. Project context lives in
[`README.md`](README.md).

The goal is to keep the app local-first, understandable, and easy to build.

The current focus is:

Priority:

- Preserve note list, note detail, and storage behavior
- Keep tests and UI test scaffolding aligned with app flow
- Avoid syncing or uploading notes without explicit design
- Keep note title normalization shared and covered by focused unit tests
- Keep note lookup guarded against stale or invalid table indexes
- Keep the local note archive protected after successful saves
- Avoid fallback archive writes when the documents path is unavailable
- Maintain build script and README context
- Keep `scripts/check-baseline.py` passing for local-first persistence,
  archive fallback behavior, storyboard guards, and note-content privacy

Next priorities:

- Strengthen tests around adding, editing, deleting, and displaying notes
- Modernize Swift/project settings in a dedicated pass
- Clarify persistence behavior and data ownership

Contribution rules:

- One PR = one focused note, UI, storage, test, or documentation change.
- Run the build script or Xcode tests before pushing behavior changes.
- Keep generated build products and signing files out of git.
- Document any change that stores or transmits note content.

## Security And Privacy

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Notes can contain sensitive personal information. The app should remain local by
default, avoid logging note content, and make any sync or export behavior
explicit.

Current baseline: `make check` runs `scripts/check-baseline.py` without Xcode.
It verifies plist/storyboard/scheme metadata, local `NoteStore.plist`
persistence, title normalization, decoded title fallback behavior, guarded note
lookup, documents path guards, archive file protection, archive fallback
behavior, and no logging, sync, analytics, upload, or network behavior in app
sources.

## What We Will Not Merge (For Now)

- Background note sync or upload without privacy design
- Note-content logging
- Broad project migration mixed with storage behavior changes
- Generated signing material

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
