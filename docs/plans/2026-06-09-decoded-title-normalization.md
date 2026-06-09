# Decoded Title Normalization

status: completed

## Context

New and edited notes normalize blank titles to `Untitled`, but archived notes
can still decode directly from stored values. Older or malformed archives with
blank title fields should use the same visible fallback as newly saved notes.

## Objectives

- Normalize decoded note titles through `Note.normalizedTitle`.
- Preserve tolerant decoding for missing text and date fields.
- Add unit coverage for archived blank titles.
- Extend the static baseline and docs to capture decoded title normalization.

## Verification

- `make check`
- `git diff --check`
