#!/usr/bin/env python3
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PLAN = ROOT / "docs/plans/2026-06-08-note-taker-baseline.md"
MAKE_GATES_PLAN = ROOT / "docs/plans/2026-06-09-make-gate-aliases.md"
FILE_PROTECTION_PLAN = ROOT / "docs/plans/2026-06-08-note-file-protection.md"
ARCHIVE_PATH_PLAN = ROOT / "docs/plans/2026-06-08-note-archive-path-guard.md"
TITLE_NORMALIZATION_PLAN = ROOT / "docs/plans/2026-06-08-note-title-normalization.md"
DECODED_TITLE_PLAN = ROOT / "docs/plans/2026-06-09-decoded-title-normalization.md"
NOTE_LOOKUP_PLAN = ROOT / "docs/plans/2026-06-09-note-lookup-index-guard.md"
DELETE_RESULT_PLAN = ROOT / "docs/plans/2026-06-09-note-delete-result-guard.md"
NAV_LOGO_PLAN = ROOT / "docs/plans/2026-06-09-navigation-logo-title-view.md"
REFERENCE_DELETE_PLAN = ROOT / "docs/plans/2026-06-10-note-reference-delete-result.md"
HOSTED_VALIDATION_PLAN = ROOT / "docs/plans/2026-06-10-hosted-project-validation.md"


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def strip_swift_line_comments(text):
    return "\n".join(line.split("//", 1)[0] for line in text.splitlines())


def require_order(text, tokens, message, failures):
    position = -1
    for token in tokens:
        next_position = text.find(token, position + 1)
        if next_position == -1:
            failures.append(message)
            return
        position = next_position


def parse_xml(relative_path, failures):
    try:
        ET.parse(str(ROOT / relative_path))
    except ET.ParseError as error:
        failures.append(f"{relative_path} is not well-formed XML: {error}")


def parse_plist(relative_path, failures):
    try:
        with (ROOT / relative_path).open("rb") as file:
            return plistlib.load(file)
    except Exception as error:
        failures.append(f"{relative_path} is not a readable plist: {error}")
        return {}


def main():
    failures = []
    required_files = [
        ".gitignore",
        ".github/workflows/check.yml",
        ".travis.yml",
        "CHANGES.md",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "build.sh",
        "NoteTaker.xcodeproj/project.pbxproj",
        "NoteTaker.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
        "NoteTaker.xcodeproj/xcshareddata/xcschemes/NoteTaker.xcscheme",
        "NoteTaker.xcodeproj/xcshareddata/xcschemes/NoteTakerTests.xcscheme",
        "NoteTaker/Info.plist",
        "NoteTaker/AppDelegate.swift",
        "NoteTaker/DetailTableViewCell.swift",
        "NoteTaker/DetailViewController.swift",
        "NoteTaker/Hex.swift",
        "NoteTaker/Note.swift",
        "NoteTaker/NoteStore.swift",
        "NoteTaker/TableViewController.swift",
        "NoteTaker/ViewController.swift",
        "NoteTaker/Base.lproj/Main.storyboard",
        "NoteTaker/Base.lproj/LaunchScreen.xib",
        "NoteTakerTests/Info.plist",
        "NoteTakerTests/NoteTakerTests.swift",
        "NoteTakerUITests/Info.plist",
        "NoteTakerUITests/NoteTakerUITests.swift",
        "docs/readme-overview.svg",
        "docs/plans/2026-06-08-note-taker-baseline.md",
        "docs/plans/2026-06-09-make-gate-aliases.md",
        "docs/plans/2026-06-08-note-file-protection.md",
        "docs/plans/2026-06-08-note-archive-path-guard.md",
        "docs/plans/2026-06-08-note-title-normalization.md",
        "docs/plans/2026-06-09-decoded-title-normalization.md",
        "docs/plans/2026-06-09-note-lookup-index-guard.md",
        "docs/plans/2026-06-09-note-delete-result-guard.md",
        "docs/plans/2026-06-09-navigation-logo-title-view.md",
        "docs/plans/2026-06-10-note-reference-delete-result.md",
        "docs/plans/2026-06-10-hosted-project-validation.md",
        "img/app.gif",
    ]

    for relative_path in required_files:
        require((ROOT / relative_path).is_file(), f"Required file missing: {relative_path}", failures)

    for xml_file in [
        "NoteTaker.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
        "NoteTaker.xcodeproj/xcshareddata/xcschemes/NoteTaker.xcscheme",
        "NoteTaker.xcodeproj/xcshareddata/xcschemes/NoteTakerTests.xcscheme",
        "NoteTaker/Base.lproj/Main.storyboard",
        "NoteTaker/Base.lproj/LaunchScreen.xib",
        "docs/readme-overview.svg",
    ]:
        parse_xml(xml_file, failures)

    app_plist = parse_plist("NoteTaker/Info.plist", failures)
    test_plist = parse_plist("NoteTakerTests/Info.plist", failures)
    ui_test_plist = parse_plist("NoteTakerUITests/Info.plist", failures)
    project = read("NoteTaker.xcodeproj/project.pbxproj")
    build = read("build.sh")
    note = read("NoteTaker/Note.swift")
    store = read("NoteTaker/NoteStore.swift")
    detail = read("NoteTaker/DetailViewController.swift")
    table = read("NoteTaker/TableViewController.swift")
    unit_tests = read("NoteTakerTests/NoteTakerTests.swift")
    hex_source = read("NoteTaker/Hex.swift")
    app_sources = "\n".join(strip_swift_line_comments(path.read_text(encoding="utf-8", errors="replace"))
                            for path in sorted((ROOT / "NoteTaker").glob("*.swift")))
    readme = read("README.md")
    vision = read("VISION.md")
    security = read("SECURITY.md")
    changes = read("CHANGES.md")
    gitignore = read(".gitignore")
    makefile = read("Makefile")
    baseline_plan = BASELINE_PLAN.read_text(encoding="utf-8") if BASELINE_PLAN.exists() else ""
    make_gates_plan = MAKE_GATES_PLAN.read_text(encoding="utf-8") if MAKE_GATES_PLAN.exists() else ""
    file_protection_plan = FILE_PROTECTION_PLAN.read_text(encoding="utf-8") if FILE_PROTECTION_PLAN.exists() else ""
    archive_path_plan = ARCHIVE_PATH_PLAN.read_text(encoding="utf-8") if ARCHIVE_PATH_PLAN.exists() else ""
    title_normalization_plan = TITLE_NORMALIZATION_PLAN.read_text(encoding="utf-8") if TITLE_NORMALIZATION_PLAN.exists() else ""
    decoded_title_plan = DECODED_TITLE_PLAN.read_text(encoding="utf-8") if DECODED_TITLE_PLAN.exists() else ""
    note_lookup_plan = NOTE_LOOKUP_PLAN.read_text(encoding="utf-8") if NOTE_LOOKUP_PLAN.exists() else ""
    delete_result_plan = DELETE_RESULT_PLAN.read_text(encoding="utf-8") if DELETE_RESULT_PLAN.exists() else ""
    nav_logo_plan = NAV_LOGO_PLAN.read_text(encoding="utf-8") if NAV_LOGO_PLAN.exists() else ""
    reference_delete_plan = REFERENCE_DELETE_PLAN.read_text(encoding="utf-8") if REFERENCE_DELETE_PLAN.exists() else ""
    hosted_validation_plan = HOSTED_VALIDATION_PLAN.read_text(encoding="utf-8") if HOSTED_VALIDATION_PLAN.exists() else ""
    workflow = read(".github/workflows/check.yml")

    require(app_plist.get("CFBundlePackageType") == "APPL",
            "NoteTaker Info.plist must remain an application plist",
            failures)
    require(test_plist.get("CFBundlePackageType") == "BNDL" and ui_test_plist.get("CFBundlePackageType") == "BNDL",
            "NoteTaker test plists must remain bundle plists",
            failures)
    for source in ["NoteStore.swift", "Note.swift", "TableViewController.swift", "DetailViewController.swift", "Hex.swift"]:
        require(source in project, f"Xcode project must keep source reference: {source}", failures)
    app_scheme = read("NoteTaker.xcodeproj/xcshareddata/xcschemes/NoteTaker.xcscheme")
    test_scheme = read("NoteTaker.xcodeproj/xcshareddata/xcschemes/NoteTakerTests.xcscheme")
    require('BlueprintName = "NoteTaker"' in app_scheme and
            'BlueprintName = "NoteTakerTests"' in test_scheme,
            "Shared Xcode schemes must remain parseable and named",
            failures)
    require("IPHONEOS_DEPLOYMENT_TARGET = 8.3;" in project and "IPHONEOS_DEPLOYMENT_TARGET = 9.3;" in project,
            "Xcode project must preserve legacy app/test deployment targets",
            failures)
    require("ENABLE_TESTABILITY = YES;" in project and "@testable import NoteTaker" in unit_tests,
            "Xcode project and unit tests must keep NoteTaker app code testable from XCTest",
            failures)

    require("Note.normalizedTitle(aDecoder.decodeObjectForKey(\"title\") as? String)" in note and
            "as? NSDate ?? NSDate()" in note,
            "Note decoding must tolerate missing or incompatible archived fields",
            failures)
    for controller_name, controller_source in {
        "TableViewController": table,
        "DetailViewController": detail,
    }.items():
        require("self.navigationItem.titleView = logoView" in controller_source and
                "navigationController?.view.addSubview(logoView)" not in controller_source and
                "bringSubviewToFront(logoView)" not in controller_source and
                "logoView.frame.origin" not in controller_source,
                f"{controller_name} must scope the mini logo to the navigation item title view",
                failures)
    require("class func normalizedTitle(title: String?) -> String" in note and
            "stringByTrimmingCharactersInSet(NSCharacterSet.whitespaceAndNewlineCharacterSet())" in note and
            'trimmedTitle.isEmpty ? "Untitled" : trimmedTitle' in note,
            "Note must expose shared title normalization for blank note titles",
            failures)
    require("notes.append(theNote)\n        save()" in store,
            "createNote must save after appending a note",
            failures)
    update_note = re.search(r"func updateNote[\s\S]+?\n    }", store)
    require(update_note is not None and "save()" in update_note.group(0),
            "updateNote must persist edited note content",
            failures)
    require("func deleteNote(index:Int) -> Bool" in store and
            "if index < 0 || index >= notes.count" in store and
            "return false" in store and
            "notes.removeAtIndex(index)\n        save()\n        return true" in store,
            "deleteNote(index:) must report success only after guarded delete saves",
            failures)
    reference_delete = re.search(r"func deleteNote\(withNote:Note\) -> Bool[\s\S]+?\n    }", store)
    require(reference_delete is not None and
            "if note === withNote" in reference_delete.group(0) and
            "notes.removeAtIndex(i)\n                save()\n                return true" in reference_delete.group(0) and
            "return false" in reference_delete.group(0),
            "deleteNote(withNote:) must report whether reference deletion removed a note",
            failures)
    require("func archiveFilePath() -> String?" in store and
            "guard let firstPath = paths.first else {\n            return nil\n        }" in store and
            "NoteStore.plist" in store,
            "archiveFilePath must return nil for missing Documents paths and use the local note archive",
            failures)
    require_order(
        store,
        [
            "guard let path = archiveFilePath() else",
            "return",
            "let archived = NSKeyedArchiver.archiveRootObject(notes, toFile: path)",
            "if archived",
            "applyFileProtection(path)",
        ],
        "save must apply file protection only after a successful archive write",
        failures,
    )
    require("func applyFileProtection(path:String)" in store and
            "NSFileProtectionKey: NSFileProtectionComplete" in store and
            "setAttributes" in store,
            "NoteStore must apply complete file protection to local note archives",
            failures)
    get_note = re.search(r"func getNote[\s\S]+?\n    }", store)
    require(get_note is not None and
            "func getNote(index:Int) -> Note?" in get_note.group(0) and
            "if index < 0 || index >= notes.count" in get_note.group(0) and
            "return nil" in get_note.group(0),
            "getNote(index:) must reject invalid note indexes instead of indexing directly",
            failures)
    require("as? [Note]" in store and "notes = [Note]()" in store,
            "load must fall back to an empty note list for invalid archives",
            failures)
    require_order(
        store,
        [
            "guard let filePath = archiveFilePath() else",
            "notes = [Note]()",
            "return",
            "let fileManager = NSFileManager.defaultManager()",
        ],
        "load must fall back to an empty note list when the Documents path is unavailable",
        failures,
    )
    require("Note.normalizedTitle(self.noteTitleLabel.text)" in detail and
            'self.noteTextView.text ?? ""' in detail,
            "DetailViewController must use shared title normalization and avoid force-unwrapping note fields",
            failures)
    require("testNoteTitleNormalizationTrimsWhitespace" in unit_tests and "XCTAssertEqual" in unit_tests and
            "testNoteTitleNormalizationDefaultsBlankTitles" in unit_tests and
            "testDecodedBlankTitleUsesVisibleFallback" in unit_tests and
            "testNoteStoreGetNoteRejectsInvalidIndexes" in unit_tests and
            "testNoteStoreDeleteNoteRejectsInvalidIndexes" in unit_tests and
            "testNoteStoreDeleteNoteByReferenceReportsResults" in unit_tests and
            "XCTAssert(true" not in unit_tests and "testPerformanceExample" not in unit_tests,
            "NoteTakerTests must replace template tests with note-title normalization assertions",
            failures)
    require("as? DetailViewController" in table and "as? DetailTableViewCell" in table and "as? DetailTableViewCell" in table,
            "TableViewController must guard storyboard casts",
            failures)
    require("if NoteStore.sharedNoteStore.deleteNote(indexPath.row)" in table and
            "tableView.deleteRowsAtIndexPaths([indexPath], withRowAnimation: .Fade)" in table,
            "TableViewController must delete visible rows only after store deletion succeeds",
            failures)
    require("guard let theNote = NoteStore.sharedNoteStore.getNote(rowNumber) else" in table and
            "return cell" in table,
            "TableViewController must use guarded note lookup before configuring cells",
            failures)
    require("return UITableViewCell()" in table,
            "TableViewController must return a fallback cell for unexpected storyboard wiring",
            failures)
    require("let scanner = NSScanner(string: cString)" in hex_source and "scanner.atEnd" in hex_source,
            "Hex parser must reject partial invalid scans",
            failures)

    require("function ci_build" not in build and "ci_build()" in build,
            "build.sh must use POSIX function syntax",
            failures)
    require("command -v xcodebuild" in build and "xcodebuild unavailable" in build,
            "build.sh must skip cleanly on hosts without Xcode",
            failures)
    require("SIMULATOR_NAME" in build,
            "build.sh must allow overriding the legacy simulator name",
            failures)
    require(not re.search(r"\b(?:print|println|NSLog)\s*\(", app_sources),
            "Note content and storage state must not be logged",
            failures)
    require("as!" not in app_sources,
            "App sources must avoid force-casts in note and storyboard flows",
            failures)
    for forbidden in ["URLSession", "NSURLConnection", "NSURL", "http://", "https://", "upload", "analytics"]:
        require(forbidden not in app_sources,
                f"Note app must not add sync, upload, analytics, or network behavior: {forbidden}",
                failures)
    swift_files = sorted((ROOT / "NoteTaker").glob("*.swift")) + sorted((ROOT / "NoteTakerTests").glob("*.swift")) + sorted((ROOT / "NoteTakerUITests").glob("*.swift"))
    require(len(swift_files) >= 10,
            "expected Swift source/test inventory is missing",
            failures)
    require("*.local.xcconfig" in gitignore and ".env" in gitignore and "DerivedData" in gitignore,
            ".gitignore must exclude local config and Xcode build products",
            failures)
    require(".PHONY: build check lint test" in makefile and "lint test build: check" in makefile,
            "Makefile must expose lint, test, and build aliases for the local baseline",
            failures)
    require("make lint" in readme and "make test" in readme and "make build" in readme and "make check" in readme and "NoteStore.plist" in readme and "local" in readme.lower() and
            "file protection" in readme.lower() and "documents path" in readme.lower() and
            "title normalization" in readme.lower() and "decoded title" in readme.lower() and
            "note lookup" in readme.lower() and "delete result" in readme.lower() and
            "reference delete" in readme.lower() and "title view" in readme.lower(),
            "README must document static verification, local note persistence, title normalization, path guards, and file protection",
            failures)
    require("scripts/check-baseline.py" in vision and "make lint" in vision and "make test" in vision and "make build" in vision and "local-first" in vision.lower() and
            "documents path" in vision.lower() and "title normalization" in vision.lower() and "title view" in vision.lower() and
            "decoded title" in vision.lower() and "note lookup" in vision.lower() and "delete result" in vision.lower() and
            "reference delete" in vision.lower(),
            "VISION must describe the current static local-first baseline",
            failures)
    require("note content" in security.lower() and "make check" in security and
            "local" in security.lower() and "title normalization" in security.lower() and "title view" in security.lower() and
            "decoded title" in security.lower() and "note lookup" in security.lower() and "delete result" in security.lower() and
            "reference delete" in security.lower(),
            "SECURITY must document note-content privacy and static baseline guardrails",
            failures)
    require("persist" in changes.lower() and "archive" in changes.lower() and "file protection" in changes.lower() and
            "documents path" in changes.lower() and "title normalization" in changes.lower() and "decoded title" in changes.lower() and
            "reference delete" in changes.lower() and "title view" in changes.lower() and "make check" in changes and "make lint" in changes and "make test" in changes and "make build" in changes,
            "CHANGES must record persistence hardening, title normalization, path guarding, file protection, and baseline",
            failures)
    require("note lookup" in changes.lower(),
            "CHANGES must record guarded note lookup updates",
            failures)
    require("delete result" in changes.lower(),
            "CHANGES must record guarded delete result updates",
            failures)
    require("status: completed" in baseline_plan and "status: completed" in file_protection_plan and
            "status: completed" in archive_path_plan and "status: completed" in title_normalization_plan,
            "plans must be marked completed",
            failures)
    require("status: completed" in make_gates_plan,
            "make gate aliases plan must be marked completed",
            failures)
    require("status: completed" in decoded_title_plan,
            "decoded title normalization plan must be marked completed",
            failures)
    require("status: completed" in note_lookup_plan,
            "note lookup index guard plan must be marked completed",
            failures)
    require("status: completed" in delete_result_plan,
            "note delete result guard plan must be marked completed",
            failures)
    require("status: completed" in nav_logo_plan,
            "navigation logo title-view plan must be marked completed",
            failures)
    require("status: completed" in reference_delete_plan,
            "note reference delete result plan must be marked completed",
            failures)
    require("status: completed" in hosted_validation_plan and "make check" in hosted_validation_plan,
            "hosted project validation plan must be completed and document make check",
            failures)
    require("permissions:\n  contents: read" in workflow,
            "Check workflow must use read-only repository permissions",
            failures)
    require("cancel-in-progress: true" in workflow and "runs-on: macos-15" in workflow and
            "timeout-minutes: 10" in workflow,
            "Check workflow must bound duplicate and long-running macOS jobs",
            failures)
    require("actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" in workflow and
            "run: make check" in workflow,
            "Check workflow must pin checkout and run the canonical baseline",
            failures)

    if shutil.which("xcodebuild"):
        result = subprocess.run(
            ["xcodebuild", "-list", "-project", "NoteTaker.xcodeproj"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        require(result.returncode == 0,
                "xcodebuild could not parse NoteTaker.xcodeproj and shared schemes: " + result.stderr.strip(),
                failures)
    else:
        print("xcodebuild unavailable; static iOS baseline only.")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("ios-note-taker baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
