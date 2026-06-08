## iOS Note Taker Vision

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
- Maintain build script and README context

Next priorities:

- Add setup and verification details for current Xcode versions
- Strengthen tests around adding, editing, deleting, and displaying notes
- Modernize Swift/project settings in a dedicated pass
- Clarify persistence behavior and data ownership

Contribution rules:

- One PR = one focused note, UI, storage, test, or documentation change.
- Run the build script or Xcode tests before pushing behavior changes.
- Keep generated build products and signing files out of git.
- Document any change that stores or transmits note content.

## Security And Privacy

Notes can contain sensitive personal information. The app should remain local by
default, avoid logging note content, and make any sync or export behavior
explicit.

## What We Will Not Merge For Now

- Background note sync or upload without privacy design
- Note-content logging
- Broad project migration mixed with storage behavior changes
- Generated signing material
