# Protected Atomic Note Write

status: planned

## Context

`NoteStore.save()` writes the secure archive atomically and applies complete file
protection afterward. The replacement archive therefore depends on a second
filesystem operation before it has the intended protection class, and a failed
attribute update can leave newly written note content less protected than
expected.

## Scope

- Request complete file protection as part of the atomic data write.
- Retain the explicit attribute update to repair existing or platform-specific
  archive metadata.
- Extend the static persistence contract with write-option ordering checks.
- Preserve secure coding, the Documents archive location, and local-only data
  behavior.

## Verification

- `make check`
- `git diff --check`
- Mutations removing complete protection from the write must fail the baseline.
- Hosted macOS validation must compile the Swift 5 note target.
