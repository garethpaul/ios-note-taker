# Delete Persistence Feedback

status: completed

## Context

`NoteStore.deleteNote` already restores a removed note when the protected
archive write fails. The table controller only removed the visible row after a
successful delete, but a failed delete produced no feedback and looked like an
unresponsive swipe action.

## Design

- Keep the store's transactional delete and rollback behavior unchanged.
- Delete the table row only after `deleteNote` reports success.
- On failure, keep the restored row visible and present a deletion-specific
  `UIAlertController` explaining that the saved note was unchanged.
- Keep note content and local paths out of the alert and logs.

## Test First

The static baseline first required deletion-specific failure presentation in
the failed branch. It failed on the unchanged controller before implementation.

## Verification

- All four Make gates passed through an isolated `uv` Python 3.9 runtime.
- `python3 scripts/check-baseline.py` passed directly.
- `python3 -m py_compile scripts/check-baseline.py scripts/test-build-helper.py`
  passed.
- Store XCTest covers failed-delete rollback and object identity; hosted push
  baseline run `28171104244` and pull-request baseline run `28171106051`
  passed on reviewed head `2db70c94e99d8c89f3ad342e878e905fa27911aa`.
- Four isolated hostile mutations were rejected: removed failure presentation,
  row deletion on failure, a misleading success alert title, and removed
  rollback-identity evidence.
- `git diff --check` passed.
- `xcodebuild` was unavailable on the local Linux host, so current-Xcode
  compilation and XCTest were verified by the hosted baselines.
- CodeQL run `28171104187` passed actions, Python, and Swift analysis.
- Codex review reported no actionable findings while its parallel Python 3.9
  Make gate passed.

## Scope Boundaries

- Successful delete animation, note contents, archive format, file protection,
  quarantine behavior, and edit/save failure handling remain unchanged.
- This change does not add logging, sync, export, analytics, or network access.

## References

- https://developer.apple.com/documentation/uikit/uitableview/deleterows%28at%3Awith%3A%29
- https://developer.apple.com/documentation/uikit/uialertcontroller
