# Changes

## 2026-06-08

- Saved notes after create, edit, and delete operations so local note changes persist.
- Applied complete file protection to the local note archive after successful saves.
- Guarded missing documents paths so saves skip fallback archive writes and loads start with an empty note list.
- Guarded archived note decoding and local archive loading so corrupt or incompatible files fall back to an empty note list.
- Trimmed blank note titles to `Untitled` and avoided force-unwrapping note text fields.
- Applied title normalization to decoded title values from archived notes.
- Moved note title normalization into the `Note` model and added focused unit assertions for it.
- Guarded note lookup so stale or invalid table indexes do not directly index the note archive.
- Guarded storyboard casts in table/detail flows and rejected invalid delete indexes.
- Rejected partial invalid hex color scans so malformed colors fall back to gray.
- Made `build.sh` POSIX-compatible, safe on hosts without Xcode, and
  configurable with `SIMULATOR_NAME`.
- Added `make check` and a static iOS note baseline for plist/storyboard/scheme XML, local persistence, source inventory, and privacy guardrails.
