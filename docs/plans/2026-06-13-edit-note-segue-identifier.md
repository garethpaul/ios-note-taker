# Edit Note Segue Identifier

status: planned

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

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile scripts/check-baseline.py`
- Parse plist, storyboard, XIB, scheme, workspace, project, and workflow
  metadata with available local parsers.
- `sh -n build.sh`
- `git diff --check`
- Hostile mutations removing, renaming, relocating, or duplicating the edit
  identifier, changing the add identifier, weakening controller guards, or
  falsifying plan evidence must be rejected.
