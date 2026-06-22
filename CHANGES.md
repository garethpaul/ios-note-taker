# Changes

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
