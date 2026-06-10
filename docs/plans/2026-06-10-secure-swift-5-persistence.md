# Secure Swift 5 Persistence

status: completed

## Context

The note app still used Swift 2-era source and deprecated unrestricted keyed
archiving. Hosted CI only parsed project metadata, so neither the existing tests
nor the local persistence path compiled under current Xcode.

## Completed Scope

- Migrated the app, unit-test, and UI-test targets to Swift 5 and iOS 12.
- Migrated `Note` from `NSCoding` to `NSSecureCoding` with class-restricted field
  decoding and existing title fallback behavior.
- Replaced `archiveRootObject` with throwing secure data archiving and atomic
  file writes.
- Restricted archive loading to the array, note, string, and date classes used
  by the persisted model; invalid archives still produce an empty store.
- Preserved complete file protection after successful writes.
- Added a secure archive round-trip unit assertion.
- Upgraded Xcode-enabled `make check` runs to compile the unsigned app and unit
  test bundle for the iOS Simulator.
- Extended the baseline and documentation to preserve the security and
  toolchain contracts.

## Verification

- `python3 scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hosted macOS app and unit-test build
- `git diff --check`
