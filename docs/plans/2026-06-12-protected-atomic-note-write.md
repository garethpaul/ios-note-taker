# Protected Atomic Note Write

status: completed

## Context

`NoteStore.save()` writes the secure archive atomically and applies complete file
protection afterward. The replacement archive therefore depends on a second
filesystem operation before it has the intended protection class, and a failed
attribute update can leave newly written note content less protected than
expected.

## Work Completed

- Request complete file protection as part of the atomic data write.
- Retain the explicit attribute update to repair existing or platform-specific
  archive metadata.
- Extend the static persistence contract with write-option ordering checks.
- Preserve secure coding, the Documents archive location, and local-only data
  behavior.

## Verification Completed

- Local `make check`, `make lint`, `make test`, and `make build` passed. The
  local environment did not provide `xcodebuild`, so these runs exercised the
  complete static baseline and reported the hosted Xcode requirement.
- `python3 -m py_compile scripts/check-baseline.py` and `git diff --check`
  passed.
- Hostile mutations changing the plan status, inserting an unfinished-work
  marker, falsifying a run ID, removing complete protection from the atomic
  write, or moving attribute repair before the write were rejected.
- The implementation push Check run `27395126378` completed successfully for
  commit `d330ffdb1557d111868248c8c1b2055b39cda02e`.
- The implementation pull-request Check run `27395135480` completed
  successfully for commit `d330ffdb1557d111868248c8c1b2055b39cda02e` and
  compiled the Swift 5 note target on hosted macOS.
- The post-merge push Check run `27395178307` completed successfully for
  commit `58f8f0bc9db12e991a6fa6116794c8a578e593d9`.
- The CodeQL setup run `27402323479` completed successfully for commit
  `58f8f0bc9db12e991a6fa6116794c8a578e593d9`.
- Persistence preserves
  `data.write(to: url, options: [.atomic, .completeFileProtection])` before
  `applyFileProtection(url.path)`.
