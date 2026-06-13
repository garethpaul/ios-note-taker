# Edit Note Segue Identifier

status: completed

## Context

`TableViewController.prepare(for:sender:)` passes the selected note only for
the `NoteDetailPush` segue. The prototype-cell show segue in `Main.storyboard`
has no identifier, so tapping an existing row opens `DetailViewController` with
its default blank note instead of the selected note.

## Priority

Editing an existing note is a primary workflow. The current storyboard and
controller contract disagree silently, causing note content to appear missing
and preventing the intended reference-backed update path.

## Requirements

- R1. Give the prototype-cell show segue the exact `NoteDetailPush` identifier.
- R2. Preserve the add-button `NoteDetailAdd` segue and save unwind action.
- R3. Preserve guarded destination and sender casts before assigning the
  selected note to the detail controller.
- R4. Parse the storyboard structurally and require the edit identifier on the
  cell-owned show segue rather than accepting an unrelated matching string.
- R5. Preserve secure local persistence, note identity, title normalization,
  delete behavior, UI layout, and local-only privacy boundaries.
- R6. Record completed local verification and hostile-mutation evidence.

## Implementation Units

### U1. Restore edit routing metadata

- **File:** `NoteTaker/Base.lproj/Main.storyboard`
- Add `identifier="NoteDetailPush"` to the existing prototype-cell show segue.

### U2. Enforce storyboard-controller agreement

- **File:** `scripts/check-baseline.py`
- Locate the prototype table cell and require its show segue to target the
  detail controller with the exact edit identifier.
- Keep separate contracts for the add segue and save unwind action.

### U3. Document the edit workflow guardrail

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Record that existing-note navigation must preserve selected-note identity.

## Scope Boundaries

- Do not change controller navigation logic, note model fields, archive format,
  file protection, table layout, or save semantics.
- Do not add sync, networking, analytics, upload, logging, or telemetry.
- Do not claim interactive simulator validation without Xcode.

## Work Completed

- Assigned `NoteDetailPush` to the prototype-cell show segue that opens the
  existing-note detail screen.
- Added a parsed storyboard contract for unique cell-owned edit routing,
  separate add routing, and the save unwind action.
- Preserved guarded controller casts and selected-note assignment.
- Documented the selected-note identity boundary across baseline guidance.

## Verification Completed

- All four Make gates, `make lint`, `make test`, `make build`, and `make check`,
  passed against the complete static baseline.
- `python3 -m py_compile scripts/check-baseline.py`, plist parsing, storyboard,
  XIB, scheme, workspace, and SVG XML parsing, workflow YAML parsing,
  `sh -n build.sh`, and `git diff --check` passed.
- Eleven hostile mutations removing, renaming, duplicating, relocating, or
  retargeting the edit segue, changing add or unwind routing, weakening the
  destination cast, replacing selected-note assignment, or falsifying plan
  status or verification evidence were rejected.
- The local environment did not provide `xcodebuild`, so interactive edit
  navigation and simulator execution were not claimed.
