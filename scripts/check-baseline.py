#!/usr/bin/env python3
import ast
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
SECURE_SWIFT_5_PLAN = ROOT / "docs/plans/2026-06-10-secure-swift-5-persistence.md"
PROTECTED_WRITE_PLAN = ROOT / "docs/plans/2026-06-12-protected-atomic-note-write.md"
EDIT_SEGUE_PLAN = ROOT / "docs/plans/2026-06-13-edit-note-segue-identifier.md"
CORRUPT_ARCHIVE_PLAN = ROOT / "docs/plans/2026-06-13-corrupt-note-archive-quarantine.md"
LOCATION_INDEPENDENT_MAKE_PLAN = ROOT / "docs/plans/2026-06-13-location-independent-make.md"
UNREADABLE_ARCHIVE_PLAN = ROOT / "docs/plans/2026-06-15-unreadable-archive-write-guard.md"


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text, heading):
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


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


def has_unsigned_simulator_build(checker):
    required_arguments = {
        "xcodebuild",
        "-project",
        "NoteTaker.xcodeproj",
        "-target",
        "NoteTakerTests",
        "-configuration",
        "Debug",
        "-sdk",
        "iphonesimulator",
        "CODE_SIGNING_ALLOWED=NO",
        "build",
    }
    try:
        tree = ast.parse(checker)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.List):
            continue
        arguments = {
            element.value
            for element in node.elts
            if isinstance(element, ast.Constant) and isinstance(element.value, str)
        }
        if required_arguments.issubset(arguments):
            return True
    return False


def has_note_detail_storyboard_contract():
    try:
        root = ET.parse(ROOT / "NoteTaker/Base.lproj/Main.storyboard").getroot()
    except (ET.ParseError, OSError):
        return False

    detail = root.find(".//viewController[@storyboardIdentifier='DetailViewController']")
    cell = root.find(".//tableViewCell[@customClass='DetailTableViewCell']")
    add_button = root.find(".//barButtonItem[@systemItem='add']")
    save_button = root.find(".//barButtonItem[@systemItem='save']")
    if detail is None or cell is None or add_button is None or save_button is None:
        return False

    detail_id = detail.get("id")
    edit_segues = root.findall(".//segue[@identifier='NoteDetailPush']")
    add_segues = root.findall(".//segue[@identifier='NoteDetailAdd']")
    cell_segues = cell.findall("./connections/segue")
    add_button_segues = add_button.findall("./connections/segue")
    save_unwinds = save_button.findall("./connections/segue")

    return (
        len(edit_segues) == 1
        and len(cell_segues) == 1
        and edit_segues[0] is cell_segues[0]
        and edit_segues[0].get("destination") == detail_id
        and edit_segues[0].get("kind") == "show"
        and len(add_segues) == 1
        and len(add_button_segues) == 1
        and add_segues[0] is add_button_segues[0]
        and add_segues[0].get("destination") == detail_id
        and add_segues[0].get("kind") == "show"
        and len(save_unwinds) == 1
        and save_unwinds[0].get("kind") == "unwind"
        and save_unwinds[0].get("unwindAction") == "saveFromNoteDetail:"
    )


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
        "scripts/test-build-helper.py",
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
        "docs/plans/2026-06-10-secure-swift-5-persistence.md",
        "docs/plans/2026-06-12-protected-atomic-note-write.md",
        "docs/plans/2026-06-13-edit-note-segue-identifier.md",
        "docs/plans/2026-06-13-corrupt-note-archive-quarantine.md",
        "docs/plans/2026-06-13-location-independent-make.md",
        "docs/plans/2026-06-15-unreadable-archive-write-guard.md",
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
    checker = read("scripts/check-baseline.py")
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
    secure_swift_5_plan = SECURE_SWIFT_5_PLAN.read_text(encoding="utf-8") if SECURE_SWIFT_5_PLAN.exists() else ""
    protected_write_plan = PROTECTED_WRITE_PLAN.read_text(encoding="utf-8") if PROTECTED_WRITE_PLAN.exists() else ""
    edit_segue_plan = EDIT_SEGUE_PLAN.read_text(encoding="utf-8") if EDIT_SEGUE_PLAN.exists() else ""
    corrupt_archive_plan = CORRUPT_ARCHIVE_PLAN.read_text(encoding="utf-8") if CORRUPT_ARCHIVE_PLAN.exists() else ""
    location_independent_make_plan = LOCATION_INDEPENDENT_MAKE_PLAN.read_text(encoding="utf-8") if LOCATION_INDEPENDENT_MAKE_PLAN.exists() else ""
    unreadable_archive_plan = UNREADABLE_ARCHIVE_PLAN.read_text(encoding="utf-8") if UNREADABLE_ARCHIVE_PLAN.exists() else ""
    workflow = read(".github/workflows/check.yml")
    test_runner = read("scripts/run-tests.sh")
    build_helper_tests = read("scripts/test-build-helper.py")

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
    require(project.count("IPHONEOS_DEPLOYMENT_TARGET = 12.0;") == 4 and
            "IPHONEOS_DEPLOYMENT_TARGET = 8.3;" not in project and
            "IPHONEOS_DEPLOYMENT_TARGET = 9.3;" not in project and
            project.count("SWIFT_VERSION = 5.0;") == 6,
            "Xcode project must use Swift 5 and iOS 12 for app and test targets",
            failures)
    require("ENABLE_TESTABILITY = YES;" in project and "@testable import NoteTaker" in unit_tests,
            "Xcode project and unit tests must keep NoteTaker app code testable from XCTest",
            failures)

    require("class Note: NSObject, NSSecureCoding" in note and
            "static var supportsSecureCoding: Bool { true }" in note and
            'decodeObject(of: NSString.self, forKey: "title") as? String' in note and
            'Note.normalizedText(coder.decodeObject(of: NSString.self, forKey: "text") as? String)' in note and
            'decodeObject(of: NSDate.self, forKey: "date") as? Date ?? Date()' in note,
            "Note decoding must tolerate missing or incompatible archived fields",
            failures)
    require("[UIApplication.LaunchOptionsKey: Any]?" in app_sources,
            "AppDelegate must use the Swift 5 launch-options signature",
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
    require("class func normalizedTitle(_ title: String?) -> String" in note and
            "trimmingCharacters(in: .whitespacesAndNewlines)" in note and
            'trimmedTitle.isEmpty ? "Untitled" : trimmedTitle' in note,
            "Note must expose shared title normalization for blank note titles",
            failures)
    require("notes.append(note)\n        _ = save()" in store,
            "createNote must save after appending a note",
            failures)
    update_note = re.search(r"func updateNote[\s\S]+?\n    }", store)
    require(update_note is not None and "save()" in update_note.group(0),
            "updateNote must persist edited note content",
            failures)
    require("func deleteNote(_ index: Int) -> Bool" in store and
            "guard notes.indices.contains(index) else" in store and
            "return false" in store and
            "let removedNote = notes.remove(at: index)" in store and
            "notes.insert(removedNote, at: index)" in store,
            "deleteNote(index:) must report success only after guarded delete saves",
            failures)
    reference_delete = re.search(r"func deleteNote\(_ note: Note\) -> Bool[\s\S]+?\n    }", store)
    require(reference_delete is not None and
            "guard let index = index(of: note)" in reference_delete.group(0) and
            "return deleteNote(index)" in reference_delete.group(0) and
            "return false" in reference_delete.group(0),
            "deleteNote(withNote:) must report whether reference deletion removed a note",
            failures)
    require("func archiveFileURL() -> URL?" in store and
            "FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)" in store and
            "NoteStore.plist" in store,
            "archiveFileURL must return nil for missing Documents paths and use the local note archive",
            failures)
    require("guard !archiveWritesBlocked, let url = archiveFileURL(), archiveURLIsSafeForWriting(url) else" in store and
            "NSKeyedArchiver.archivedData(withRootObject: notes, requiringSecureCoding: true)" in store and
            "try archiveDataWriter(data, url)" in store and
            "O_EXCL | O_NOFOLLOW" in store and
            "fsync(descriptor)" in store and
            "rename(temporaryURL.path, destinationURL.path)" in store and
            "synchronizeDirectory(directoryURL)" in store,
        "save must securely archive, atomically write protected note data, and repair attributes",
        failures,
    )
    require("func applyFileProtection(to url: URL) throws" in store and
            ".protectionKey: FileProtectionType.complete" in store and
            ".posixPermissions: 0o600" in store and
            "setAttributes" in store,
            "NoteStore must apply complete file protection to local note archives",
            failures)
    get_note = re.search(r"func getNote[\s\S]+?\n    }", store)
    require(get_note is not None and
            "func getNote(_ index: Int) -> Note?" in get_note.group(0) and
            "guard notes.indices.contains(index) else" in get_note.group(0) and
            "return nil" in get_note.group(0),
            "getNote(index:) must reject invalid note indexes instead of indexing directly",
            failures)
    require("private var archiveWritesBlocked = false" in store and
            "data = try archiveDataLoader(fileURL)" in store and
            "archiveWritesBlocked = true" in store and
            "values.isSymbolicLink != true" in store,
            "load must block writes only when an existing archive cannot be read",
            failures)
    require("let allowedClasses: [AnyClass] = [NSArray.self, Note.self, NSString.self, NSDate.self]" in store and
            "guard let decodedNotes = try NSKeyedUnarchiver.unarchivedObject(" in store and
            ") as? [Note], decodedNotes.count <= NoteStore.maximumNoteCount else {" in store and
            store.count("archiveWritesBlocked = !quarantineCorruptArchive(fileURL)") >= 2 and
            "notes = decodedNotes\n            archiveWritesBlocked = false" in store,
            "load must quarantine thrown and wrong-root secure decode failures",
            failures)
    require("func quarantineCorruptArchive(_ archiveURL: URL) -> Bool" in store and
            "NoteStore.corrupt.plist" in store and
            "NoteStore.corrupt-\\(UUID().uuidString).plist" in store and
            "try FileManager.default.moveItem(at: archiveURL, to: quarantineURL)" in store and
            "try NoteStore.applyFileProtection(to: quarantineURL)" in store and
            "return false" in store,
            "corrupt archive quarantine must report whether the live path is safe to replace",
            failures)
    require_order(
        store,
        [
            "guard let fileURL = archiveFileURL() else",
            "notes = []",
            "archiveWritesBlocked = true",
            "return",
            "archiveDataLoader(fileURL)",
        ],
        "load must fall back to an empty note list when the Documents path is unavailable",
        failures,
    )
    require("Note.normalizedTitle(noteTitleLabel.text)" in detail and
            "Note.normalizedText(noteTextView.text)" in detail and
            "func normalizedInput()" in detail,
            "DetailViewController must use shared title normalization and avoid force-unwrapping note fields",
            failures)
    require("testNoteTitleNormalizationTrimsWhitespace" in unit_tests and "XCTAssertEqual" in unit_tests and
            "testNoteTitleNormalizationDefaultsBlankTitles" in unit_tests and
            "testDecodedBlankTitleUsesVisibleFallback" in unit_tests and
            "testSecureArchiveRoundTripPreservesNoteFields" in unit_tests and
            "requiringSecureCoding: true" in unit_tests and
            "testNoteStoreGetNoteRejectsInvalidIndexes" in unit_tests and
            "testNoteStoreDeleteNoteRejectsInvalidIndexes" in unit_tests and
            "testNoteStoreDeleteNoteByReferenceReportsResults" in unit_tests and
            "testReadableCorruptArchiveIsQuarantined" in unit_tests and
            "testWrongArchiveRootTypeIsQuarantined" in unit_tests and
            "testValidArchiveRemainsAtLivePath" in unit_tests and
            "testUnreadableExistingArchiveBlocksReplacementUntilSuccessfulReload" in unit_tests and
            "testMissingArchiveAllowsFirstWrite" in unit_tests and
            "XCTAssertEqual(try Data(contentsOf: urls.archive), originalData)" in unit_tests and
            "XCTAssert(true" not in unit_tests and "testPerformanceExample" not in unit_tests,
            "NoteTakerTests must replace template tests with note-title normalization assertions",
            failures)
    require("as? DetailViewController" in table and "as? DetailTableViewCell" in table and "as? DetailTableViewCell" in table,
            "TableViewController must guard storyboard casts",
            failures)
    require('segue.identifier == "NoteDetailPush"' in table and
            "noteDetail.theNote = theNote" in table and
            has_note_detail_storyboard_contract(),
            "Storyboard edit routing must pass the selected note through the unique cell-owned NoteDetailPush segue",
            failures)
    require("if NoteStore.sharedNoteStore.deleteNote(indexPath.row)" in table and
            "tableView.deleteRows(at: [indexPath], with: .fade)" in table,
            "TableViewController must delete visible rows only after store deletion succeeds",
            failures)
    require("guard let theNote = NoteStore.sharedNoteStore.getNote(rowNumber) else" in table and
            "return cell" in table,
            "TableViewController must use guarded note lookup before configuring cells",
            failures)
    require("return UITableViewCell()" in table,
            "TableViewController must return a fallback cell for unexpected storyboard wiring",
            failures)
    require("let scanner = Scanner(string: cString)" in hex_source and "scanner.isAtEnd" in hex_source,
            "Hex parser must reject partial invalid scans",
            failures)

    require("command -v xcodebuild" in build and "xcodebuild unavailable" in build,
            "build.sh must skip cleanly on hosts without Xcode",
            failures)
    require('ROOT=$(CDPATH=\'\' cd -- "$(dirname -- "$0")" && pwd)' in build and
            'xcodebuild -project "$ROOT/NoteTaker.xcodeproj"' in build and
            '-scheme "NoteTaker"' in build,
            "build.sh must resolve the checkout root and preserve the NoteTaker project and scheme",
            failures)
    require("xcrun simctl list devices available -j" in build and
            'xcrun simctl list devices available -j > "$devices_json"' in build and
            'exit "$xcrun_status"' in build and
            "Unable to list available iOS simulators." in build and
            "SIMULATOR_NAME" in build and
            'platform=iOS Simulator,id=$simulator_udid' in build and
            "No available iPhone simulator" in build and
            "iPhone 5" not in build,
            "build.sh must preserve discovery failures and select an available iPhone without a retired hard-coded device",
            failures)
    require("test_selects_latest_available_iphone_and_preserves_build_authority" in build_helper_tests and
            "test_name_override_resolves_on_latest_matching_runtime" in build_helper_tests and
            "test_fails_clearly_without_an_available_iphone" in build_helper_tests and
            "test_preserves_xcrun_failure_before_parsing_valid_json" in build_helper_tests and
            "test_rejects_malformed_discovery_json_before_building" in build_helper_tests and
            "test_rejects_missing_discovery_fields_before_building" in build_helper_tests and
            "test_fails_clearly_for_an_unmatched_name_override" in build_helper_tests and
            "test_breaks_newest_runtime_ties_by_name_then_udid" in build_helper_tests,
            "build helper tests must cover selection, overrides, authority, discovery/parser failures, and tie-breaking",
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
    require(".PHONY: build check lint test" in makefile and
            "override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile and
            "lint test build: check" in makefile and
            'python3 "$(ROOT)/scripts/test-build-helper.py"' in makefile and
            'python3 "$(ROOT)/scripts/check-baseline.py"' in makefile and
            "python3 scripts/check-baseline.py" not in makefile,
            "Makefile must expose location-independent aliases and the focused build-helper contract",
            failures)
    require("make lint" in readme and "make test" in readme and "make build" in readme and "make check" in readme and "NoteStore.plist" in readme and "local" in readme.lower() and
            "file protection" in readme.lower() and "documents path" in readme.lower() and
            "title normalization" in readme.lower() and "decoded title" in readme.lower() and
            "note lookup" in readme.lower() and "delete result" in readme.lower() and
            "reference delete" in readme.lower() and "title view" in readme.lower() and
            "selected-note identity" in readme.lower(),
            "README must document static verification, local note persistence, title normalization, path guards, and file protection",
            failures)
    require("scripts/check-baseline.py" in vision and "make lint" in vision and "make test" in vision and "make build" in vision and "local-first" in vision.lower() and
            "documents path" in vision.lower() and "title normalization" in vision.lower() and "title view" in vision.lower() and
            "decoded title" in vision.lower() and "note lookup" in vision.lower() and "delete result" in vision.lower() and
            "reference delete" in vision.lower() and "selected-note identity" in vision.lower(),
            "VISION must describe the current static local-first baseline",
            failures)
    require("note content" in security.lower() and "make check" in security and
            "local" in security.lower() and "title normalization" in security.lower() and "title view" in security.lower() and
            "decoded title" in security.lower() and "note lookup" in security.lower() and "delete result" in security.lower() and
            "reference delete" in security.lower() and "selected-note identity" in security.lower(),
            "SECURITY must document note-content privacy and static baseline guardrails",
            failures)
    require("persist" in changes.lower() and "archive" in changes.lower() and "file protection" in changes.lower() and
            "documents path" in changes.lower() and "title normalization" in changes.lower() and "decoded title" in changes.lower() and
            "reference delete" in changes.lower() and "title view" in changes.lower() and
            "selected-note identity" in changes.lower() and "make check" in changes and
            "make lint" in changes and "make test" in changes and "make build" in changes,
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
    require("status: completed" in hosted_validation_plan and "make check" in hosted_validation_plan and
            "Python 3.12" in hosted_validation_plan and "credential persistence" in hosted_validation_plan,
            "hosted project validation plan must document completion, Python 3.12, and credential handling",
            failures)
    require("status: completed" in secure_swift_5_plan and "NSSecureCoding" in secure_swift_5_plan,
            "secure Swift 5 persistence plan must be completed and document NSSecureCoding",
            failures)
    require("status: completed" in edit_segue_plan and
            "All four Make gates" in edit_segue_plan and
            "hostile mutations" in edit_segue_plan.lower(),
            "edit note segue plan must record completed status and verification",
            failures)
    location_make_statuses = re.findall(
        r"^status: .+$", location_independent_make_plan, flags=re.MULTILINE
    )
    location_make_verification = markdown_section(
        location_independent_make_plan, "Verification Completed"
    )
    require(location_make_statuses == ["status: completed"] and
            "All four Make gates passed from the checkout" in location_make_verification and
            "All four Make gates passed from `/tmp` through the absolute Makefile path" in location_make_verification and
            "python3 -m py_compile scripts/check-baseline.py" in location_make_verification and
            "sh -n build.sh" in location_make_verification and
            "project metadata parsing" in location_make_verification and
            "git diff --check" in location_make_verification and
            "`xcodebuild` was unavailable" in location_make_verification and
            "Five isolated hostile mutations were rejected" in location_make_verification and
            re.search(r"\b(?:pending|todo|tbd|not run)\b",
                      location_make_verification,
                      re.IGNORECASE) is None,
            "location-independent Make plan must record completed status and actual local verification",
            failures)
    require("corrupt archive quarantine" in readme.lower() and
            "corrupt archive quarantine" in security.lower() and
            "quarantine only readable corrupt" in vision.lower() and
            "corrupt archive quarantine" in changes.lower(),
            "Docs must record readable corrupt archive quarantine",
            failures)
    unreadable_archive_guidance = "Unreadable existing note archives block persistence writes until a successful secure load or completed corrupt-archive quarantine makes replacement safe."
    require(all(unreadable_archive_guidance in document for document in
                [readme, security, vision, changes, read("AGENTS.md")]),
            "Docs must record unreadable archive write blocking",
            failures)
    require("absolute makefile path" in readme.lower() and
            "location-independent" in changes.lower(),
            "README and CHANGES must document location-independent Make verification",
            failures)
    corrupt_archive_statuses = re.findall(
        r"^status: .+$", corrupt_archive_plan, flags=re.MULTILINE
    )
    corrupt_archive_sections = corrupt_archive_plan.split(
        "## Verification Completed\n", 1
    )
    corrupt_archive_verification = (
        corrupt_archive_sections[1]
        if len(corrupt_archive_sections) == 2 else ""
    )
    corrupt_archive_required_evidence = (
        "All four Make gates",
        "`xcodebuild` was",
        "python3 -m py_compile scripts/check-baseline.py",
        "sh -n build.sh",
        "plist, storyboard, XIB, scheme, workspace, SVG, and workflow YAML parsing",
        "git diff --check",
        "Seven isolated hostile mutations",
    )
    require(corrupt_archive_statuses == ["status: completed"]
            and all(item in corrupt_archive_verification
                    for item in corrupt_archive_required_evidence)
            and re.search(r"\b(?:pending|todo|tbd|not run)\b",
                          corrupt_archive_verification,
                          re.IGNORECASE) is None,
            "corrupt note archive quarantine plan must record completed status and actual local verification",
            failures)
    unreadable_archive_statuses = re.findall(
        r"^status: .+$", unreadable_archive_plan, flags=re.MULTILINE
    )
    unreadable_archive_verification = markdown_section(
        unreadable_archive_plan, "Verification Completed"
    )
    unreadable_archive_required = (
        "All four Make gates passed",
        "absolute Makefile passed from `/tmp`",
        "python3 -m py_compile scripts/check-baseline.py",
        "hostile mutations were rejected",
        "changed-line credential scan passed",
        "hosted pull-request and security-alert snapshot",
    )
    require(unreadable_archive_statuses == ["status: completed"] and
            all(item in unreadable_archive_verification
                for item in unreadable_archive_required) and
            re.search(r"\b(?:pending|todo|tbd|not run)\b",
                      unreadable_archive_verification,
                      re.IGNORECASE) is None,
            "unreadable archive write-guard plan must record completed verification",
            failures)
    protected_write_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", protected_write_plan
    )
    protected_write_work = markdown_section(protected_write_plan, "Work Completed")
    protected_write_verification = markdown_section(
        protected_write_plan, "Verification Completed"
    )
    require(protected_write_status == ["completed"] and protected_write_work,
            "protected atomic note write plan must record one completed status and completed work",
            failures)
    require(protected_write_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", protected_write_verification),
            "protected atomic note write plan must record finished verification without pending markers",
            failures)
    for evidence in [
        "make check",
        "make lint",
        "make test",
        "make build",
        "python3 -m py_compile scripts/check-baseline.py",
        "git diff --check",
        "27395126378",
        "27395135480",
        "27395178307",
        "27402323479",
        "d330ffdb1557d111868248c8c1b2055b39cda02e",
        "58f8f0bc9db12e991a6fa6116794c8a578e593d9",
        "data.write(to: url, options: [.atomic, .completeFileProtection])",
        "applyFileProtection(url.path)",
    ]:
        require(evidence in protected_write_verification,
                f"protected atomic note write plan must preserve verification evidence: {evidence}",
                failures)
    require(workflow.count("permissions:\n  contents: read") == 1 and
            not re.search(r"(?m)^\s{2,}permissions:\s*$", workflow) and
            not re.search(r"(?m)^\s+[A-Za-z0-9_-]+:\s*write\s*$", workflow),
            "Check workflow must use one top-level read-only permissions block",
            failures)
    require("cancel-in-progress: true" in workflow and "runs-on: macos-15" in workflow and
            "timeout-minutes: 10" in workflow,
            "Check workflow must bound duplicate and long-running macOS jobs",
            failures)
    require(workflow.count("uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10") == 1 and
            "persist-credentials: false" in workflow and
            workflow.count("uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065") == 1 and
            'python-version: "3.12"' in workflow and
            "run: make check" in workflow,
            "Check workflow must pin credential-free checkout and Python 3.12 before running the canonical baseline",
            failures)
    require("./scripts/run-tests.sh" in workflow and
            "-scheme NoteTakerTests" in test_runner and
            "-parallel-testing-enabled NO" in test_runner and
            "CODE_SIGNING_ALLOWED=NO" in test_runner,
            "Hosted Check must execute the native XCTest suite on an available iPhone simulator",
            failures)
    require(has_unsigned_simulator_build(checker),
            "Checker must preserve the unsigned NoteTakerTests simulator build command",
            failures)

    if shutil.which("xcodebuild"):
        result = subprocess.run(
            [
                "xcodebuild",
                "-project", "NoteTaker.xcodeproj",
                "-target", "NoteTakerTests",
                "-configuration", "Debug",
                "-sdk", "iphonesimulator",
                "CODE_SIGNING_ALLOWED=NO",
                "build",
            ],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        require(result.returncode == 0,
                "xcodebuild could not compile NoteTaker and its unit tests for the simulator: " + result.stdout.strip(),
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
