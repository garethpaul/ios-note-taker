# AGENTS.md

## Repository purpose

`garethpaul/ios-note-taker` is an Apple platform application or Swift sample. A simple note taker for ios

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `NoteTaker.xcodeproj` - Xcode project
- `img` - repository source or sample assets
- `NoteTaker` - repository source or sample assets
- `NoteTakerTests` - repository source or sample assets
- `NoteTakerUITests` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Local Apple development: `open NoteTaker.xcodeproj`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Swift (10), shell (1).
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- Test-related files detected: `NoteTaker.xcodeproj/xcshareddata/xcschemes/NoteTakerTests.xcscheme`, `NoteTaker/NoteStore.swift`, `NoteTakerTests/NoteTakerTests.swift`, `NoteTakerUITests/NoteTakerUITests.swift`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- Keep signing files, local xcconfig files, and environment files out of git.
- Notes can contain sensitive personal information. Keep note content local by default, avoid logging note content, and require explicit design before adding sync, upload, analytics, or export behavior.
- Unreadable existing note archives block persistence writes until a successful secure load or completed corrupt-archive quarantine makes replacement safe.
- `scripts/check-baseline.py` verifies protected atomic local persistence saves, explicit archive file-protection repair, archive fallback behavior, storyboard cast guards, invalid hex fallback, and static privacy guardrails.
- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
