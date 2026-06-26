# Changes

## 2026-06-26 14:55 PDT - P1 - Roll back failed legacy note updates

### Summary

Made `updateNote(theNote:)` restore the same note object's last successfully
persisted title and text when the protected archive write fails.

### Work completed

- Added per-object persisted content snapshots refreshed only after successful
  load or save.
- Restored title and text after legacy update failure while preserving identity,
  date, normalization, archive format, and newer edit APIs.
- Added focused XCTest and four hostile portable mutations.

### Validation

- The native regression was written first; local Xcode is unavailable.
- The portable contract failed on the missing snapshot rollback before
  implementation and passed afterward.
- Hostile mutations removing snapshot lookup, title rollback, text rollback,
  or successful-save snapshot refresh all failed closed.
- All four Python 3.9 Make aliases and the external-Makefile `check` gate passed,
  including eight build-helper cases and the complete static baseline.
- Python compilation and `git diff --check` passed.
- Hosted Xcode/XCTest and exact-head review remain the final pre-merge gates.

### Bugs / findings

- P1: the legacy update API returned false on write failure but left unsaved
  mutated fields in the in-memory store.

### Next action

- Run all local gates, exact-head review, and hosted Xcode/XCTest before merge.

## 2026-06-26 - P1 - Make convenience creation transactional

- Routed `createNote` through `persistNewNote` while preserving its return type.
- Added XCTest proving a failed archive write leaves the returned note outside
  the store rather than retaining unsaved in-memory state.
- Added mutation-sensitive source, test, plan, and privacy contracts.

## 2026-06-25 05:44 - P1 - Explain failed note deletions

### Summary
Kept transactionally restored notes visible and added deletion-specific local
feedback when the protected archive cannot persist a delete.

### Work completed
- Added an explicit failed branch to table-row deletion handling.
- Presented a content-free alert stating that the saved note was unchanged.
- Added XCTest coverage for failed-delete rollback and note identity.
- Added a mutation-sensitive static controller contract and completed plan.
- Tightened the contract after a removed-call mutation showed that a helper
  declaration alone could satisfy the first source check.
- Limited row deletion to the single success branch after a failure-branch row
  deletion mutation exposed another false pass.

### Threads
- Started: none — work completed directly in the current repository.
- Continued: none.
- Stopped: none.

### Files changed
- `NoteTaker/TableViewController.swift` — reports failed deletion persistence.
- `NoteTakerTests/NoteTakerTests.swift` — covers transactional delete rollback.
- `scripts/check-baseline.py` — enforces failure feedback and plan evidence.
- Documentation and plan files — record user-visible and privacy behavior.

### Validation
- `python3 scripts/check-baseline.py` — failed on the missing feedback contract
  before implementation and passed afterward.
- `make lint`, `make test`, `make build`, and `make check` — passed through an
  isolated `uv` Python 3.9 runtime; `xcodebuild` was unavailable locally.
- Four isolated hostile mutations removing feedback, deleting the restored row,
  using misleading copy, or weakening rollback evidence were rejected.
- Python compilation and `git diff --check` — passed.
- Codex review — clean with no actionable findings; its parallel Python 3.9
  Make gate passed.
- Hosted push baseline run `28171104244`, pull-request baseline run
  `28171106051`, and CodeQL run `28171104187` passed on reviewed head
  `2db70c94e99d8c89f3ad342e878e905fa27911aa`, including Swift XCTest/build
  and actions, Python, and Swift analysis.

### Bugs / findings
- P1: a failed protected archive delete restored the note correctly but gave no
  user feedback, making the swipe action appear broken.

### Blockers
- Current-Xcode compilation and XCTest require hosted macOS because the local
  Linux host has no `xcodebuild`.

### Next action
- Revalidate the evidence-only amendment, then merge PR #13 on exact green head.

## 2026-06-21

- Replaced the retired `iPhone 5` build-helper default with deterministic
  available-iPhone simulator selection and an offline behavior contract.
- Preserved simulator discovery failures before JSON parsing and covered
  malformed discovery output, missing fields, overrides, and deterministic ties.
- Kept the build-helper contract executable with the documented macOS Python
  3.9 runtime and added direct runtime compatibility regression checks.

## 2026-06-15

- Unreadable existing note archives block persistence writes until a successful secure load or completed corrupt-archive quarantine makes replacement safe.

## 2026-06-13

- Made all Make verification aliases location-independent when invoked through
  an absolute Makefile path.
- Added protected corrupt archive quarantine after readable note data fails
  secure decoding, while leaving unreadable protected archives in place.
- Restored selected-note identity by assigning `NoteDetailPush` to the
  prototype-cell segue used to edit existing notes.

## 2026-06-12

- Requested complete file protection as part of each atomic secure note archive
  write, while retaining explicit attribute repair.

## 2026-06-10

- Migrated app, unit-test, and UI-test targets from Swift 2-era syntax to Swift 5
  with an iOS 12 deployment target.
- Migrated notes to `NSSecureCoding` with class-restricted decoding.
- Replaced legacy file archiving with throwing secure archiving and atomic data
  writes before applying complete file protection.
- Added a secure archive round-trip unit assertion.
- Upgraded Xcode-enabled validation from project parsing to unsigned simulator
  builds of the app and unit-test targets.
- Added reference delete result handling so object-based note deletes report
  whether they actually removed and saved a note.
- Added pinned, read-only macOS CI with Python 3.12 and no persisted checkout
  credentials for the canonical `make check` baseline.
- Made Xcode-enabled checks parse `NoteTaker.xcodeproj` and its shared schemes
  without opening note archives or accessing local note content.

## 2026-06-09

- Added local `make lint`, `make test`, and `make build` gate aliases for the
  static note persistence baseline.
- Added delete result handling so invalid note deletes leave the store and table
  view unchanged.
- Scoped the mini logo to each navigation item title view instead of adding
  navigation-controller overlay subviews.

## 2026-06-08

- Saved notes after create, edit, and delete operations so local note changes persist.
- Applied complete file protection to the local note archive after successful saves.
- Guarded missing documents paths so saves skip fallback archive writes and loads start with an empty note list.
- Guarded archived note decoding and local archive loading so corrupt or incompatible files fall back to an empty note list.
- Trimmed blank note titles to `Untitled` and avoided force-unwrapping note text fields.
- Applied title normalization to decoded title values from archived notes.
- Moved note title normalization into the `Note` model and added focused unit assertions for it.
- Guarded note lookup so stale or invalid table indexes do not directly index the note archive.
- Guarded storyboard casts in table/detail flows and rejected invalid delete indexes.
- Rejected partial invalid hex color scans so malformed colors fall back to gray.
- Made `build.sh` POSIX-compatible, safe on hosts without Xcode, and
  configurable with `SIMULATOR_NAME`.
- Added `make check` and a static iOS note baseline for plist/storyboard/scheme XML, local persistence, source inventory, and privacy guardrails.
