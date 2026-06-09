# Navigation Logo Title View

status: completed

## Context

The table and detail screens each created the mini logo and added it directly to
the navigation controller's view. Re-entering screens could stack duplicate
overlay subviews outside each controller's normal navigation item lifecycle.

## Completed Scope

- Scoped the table and detail mini logos to `navigationItem.titleView`.
- Removed manual navigation-controller overlay insertion and fronting.
- Kept the logo image, size, and tint behavior unchanged.
- Extended the static baseline and docs so the mini logo stays owned by each
  controller's navigation item title view.

## Verification

- `make check`
- `git diff --check`
