//
//  NoteTakerTests.swift
//  NoteTakerTests
//
//  Created by Gareth Jones  on 6/1/15.
//  Copyright (c) 2015 gpj. All rights reserved.
//

import UIKit
import XCTest
@testable import NoteTaker

class NoteTakerTests: XCTestCase {

    private func temporaryArchiveURLs() throws -> (directory: URL, archive: URL, quarantine: URL) {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        return (
            directory,
            directory.appendingPathComponent("NoteStore.plist"),
            directory.appendingPathComponent("NoteStore.corrupt.plist")
        )
    }

    func testNoteTitleNormalizationTrimsWhitespace() {
        XCTAssertEqual(Note.normalizedTitle("  Groceries\n"), "Groceries", "Note titles should be trimmed before saving")
    }

    func testNoteTitleNormalizationDefaultsBlankTitles() {
        XCTAssertEqual(Note.normalizedTitle("  \n\t  "), "Untitled", "Blank note titles should use the visible fallback")
        XCTAssertEqual(Note.normalizedTitle(nil), "Untitled", "Missing note titles should use the visible fallback")
    }

    func testDecodedBlankTitleUsesVisibleFallback() throws {
        let note = Note()
        note.title = "  \n\t  "
        note.text = "body"

        let data = try NSKeyedArchiver.archivedData(withRootObject: note, requiringSecureCoding: true)
        let decodedNote = try NSKeyedUnarchiver.unarchivedObject(ofClass: Note.self, from: data)

        XCTAssertEqual(decodedNote?.title, "Untitled", "Archived blank note titles should use the visible fallback")
    }

    func testSecureArchiveRoundTripPreservesNoteFields() throws {
        let note = Note()
        note.title = "Groceries"
        note.text = "Milk"

        let data = try NSKeyedArchiver.archivedData(withRootObject: note, requiringSecureCoding: true)
        let decodedNote = try NSKeyedUnarchiver.unarchivedObject(ofClass: Note.self, from: data)

        XCTAssertEqual(decodedNote?.title, "Groceries")
        XCTAssertEqual(decodedNote?.text, "Milk")
        XCTAssertEqual(decodedNote?.date, note.date)
    }

    func testReadableCorruptArchiveIsQuarantined() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        let corruptData = Data("not an archive".utf8)
        try corruptData.write(to: urls.archive)

        let store = NoteStore(archiveURL: urls.archive)

        XCTAssertEqual(store.count(), 0)
        XCTAssertFalse(FileManager.default.fileExists(atPath: urls.archive.path))
        XCTAssertEqual(try Data(contentsOf: urls.quarantine), corruptData)
    }

    func testWrongArchiveRootTypeIsQuarantined() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        let data = try NSKeyedArchiver.archivedData(
            withRootObject: NSString(string: "not notes"),
            requiringSecureCoding: true
        )
        try data.write(to: urls.archive)

        let store = NoteStore(archiveURL: urls.archive)

        XCTAssertEqual(store.count(), 0)
        XCTAssertFalse(FileManager.default.fileExists(atPath: urls.archive.path))
        XCTAssertTrue(FileManager.default.fileExists(atPath: urls.quarantine.path))
    }

    func testValidArchiveRemainsAtLivePath() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        let note = Note()
        note.title = "Private"
        let data = try NSKeyedArchiver.archivedData(
            withRootObject: [note],
            requiringSecureCoding: true
        )
        try data.write(to: urls.archive)

        let store = NoteStore(archiveURL: urls.archive)

        XCTAssertEqual(store.count(), 1)
        XCTAssertTrue(FileManager.default.fileExists(atPath: urls.archive.path))
        XCTAssertFalse(FileManager.default.fileExists(atPath: urls.quarantine.path))
    }

    func testNoteStoreGetNoteRejectsInvalidIndexes() {
        let store = NoteStore.sharedNoteStore

        XCTAssertNil(store.getNote(-1), "Negative note indexes should be ignored")
        XCTAssertNil(store.getNote(store.count()), "Out-of-range note indexes should be ignored")
    }

    func testNoteStoreDeleteNoteRejectsInvalidIndexes() {
        let store = NoteStore.sharedNoteStore
        let startingCount = store.count()

        XCTAssertFalse(store.deleteNote(-1), "Negative note indexes should not delete notes")
        XCTAssertFalse(store.deleteNote(store.count()), "Out-of-range note indexes should not delete notes")
        XCTAssertEqual(store.count(), startingCount, "Invalid note deletes should leave the local note list unchanged")
    }

    func testNoteStoreDeleteNoteByReferenceReportsResults() {
        let store = NoteStore.sharedNoteStore
        let note = store.createNote(Note())
        let countAfterCreate = store.count()

        XCTAssertTrue(store.deleteNote(note), "Reference deletes should report success when a note is removed")
        XCTAssertEqual(store.count(), countAfterCreate - 1, "Successful reference deletes should remove one note")
        XCTAssertFalse(store.deleteNote(note), "Deleting the same note reference twice should report failure")
    }

}
