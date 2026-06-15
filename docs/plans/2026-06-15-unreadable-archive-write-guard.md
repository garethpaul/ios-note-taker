# Guard Writes After Unreadable Archive Loads

status: planned

## Context

`NoteStore.load()` intentionally preserves an existing archive when
`Data(contentsOf:)` cannot read it, but it resets in-memory notes to an empty
array. A later create, update, or delete calls `save()` and may atomically
replace the preserved archive with that empty or partial in-memory state. This
turns a temporary protection or I/O failure into permanent note loss.

## Requirements

- R1. Distinguish a missing first-run archive from an existing archive that
  could not be read.
- R2. Block persistence writes after an unreadable-existing-archive load so the
  preserved archive cannot be replaced by empty or partial state.
- R3. Keep in-memory CRUD behavior available while writes are blocked.
- R4. Clear the write block after a later successful secure decode.
- R5. Clear the write block after a readable corrupt archive is quarantined,
  because the original path is then safe for a new archive.
- R6. Preserve secure class-restricted decoding, atomic complete-protection
  writes, corrupt quarantine, guarded edit/delete routing, and local-only note
  privacy.
- R7. Add mutation-sensitive source, behavioral, guidance, and completed-plan
  contracts.

## Implementation Units

### U1. Persistence write state

- **File:** `NoteTaker/NoteStore.swift`
- Track whether the current archive path is unsafe to replace because an
  existing file could not be read.
- Return from `save()` before encoding or writing while that state is active.
- Reset the state on missing archive, successful decode, and completed corrupt
  quarantine.

### U2. Regression coverage

- **Files:** `NoteTakerTests/NoteTakerTests.swift`, `scripts/check-baseline.py`
- Prove a read failure for an existing archive activates the write guard while
  a missing archive and a quarantined corrupt archive remain writable.
- Add source-level contracts for guard ordering and transitions.

### U3. Maintenance evidence

- **Files:** `AGENTS.md`, `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Record that unreadable existing archives remain write-protected until a safe
  load or quarantine transition.

## Scope Boundaries

- Do not add cloud sync, encryption keys, recovery UI, background retries,
  migrations, new archive formats, or analytics.
- Do not alter note fields, segue identifiers, table routing, or corrupt-file
  quarantine naming.
- Do not edit project metadata, lockfiles, workflows, or generated artifacts.

## Verification Plan

- Run all four Make gates and the absolute Makefile from `/tmp`.
- Compile the Python checker and validate `build.sh` shell syntax.
- Reject mutations that remove existing-file detection, the early save guard,
  successful-load reset, quarantine reset, behavioral coverage, guidance, or
  completed-plan evidence.
- Audit exact intended paths, generated artifacts, project/lockfile/workflow
  exclusions, conflict markers, whitespace, and changed-line credential
  patterns.
- Push a stacked pull request and take one bounded exact-head hosted and
  security-alert snapshot without polling.
