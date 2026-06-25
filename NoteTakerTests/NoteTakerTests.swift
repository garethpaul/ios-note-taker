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

        let note = store.createNote()
        note.title = "Recovered"
        store.updateNote(theNote: note)
        XCTAssertTrue(FileManager.default.fileExists(atPath: urls.archive.path))
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

    func testUnreadableExistingArchiveBlocksReplacementUntilSuccessfulReload() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        let originalNote = Note()
        originalNote.title = "Protected"
        let originalData = try NSKeyedArchiver.archivedData(
            withRootObject: [originalNote],
            requiringSecureCoding: true
        )
        try originalData.write(to: urls.archive)
        var shouldFailRead = true
        let store = NoteStore(archiveURL: urls.archive) { url in
            if shouldFailRead {
                throw CocoaError(.fileReadNoPermission)
            }
            return try Data(contentsOf: url)
        }

        _ = store.createNote()
        XCTAssertEqual(try Data(contentsOf: urls.archive), originalData)

        shouldFailRead = false
        store.load()
        XCTAssertEqual(store.count(), 1)
        _ = store.createNote()

        let allowedClasses: [AnyClass] = [NSArray.self, Note.self, NSString.self, NSDate.self]
        let decodedNotes = try NSKeyedUnarchiver.unarchivedObject(
            ofClasses: allowedClasses,
            from: Data(contentsOf: urls.archive)
        ) as? [Note]
        XCTAssertEqual(decodedNotes?.count, 2)
    }

    func testMissingArchiveAllowsFirstWrite() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        let store = NoteStore(archiveURL: urls.archive)

        _ = store.createNote()

        XCTAssertTrue(FileManager.default.fileExists(atPath: urls.archive.path))
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

    func testFailedDeleteRestoresTheSavedNote() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        var shouldFailWrite = false
        let store = NoteStore(
            archiveURL: urls.archive,
            archiveDataWriter: { data, url in
                if shouldFailWrite {
                    throw CocoaError(.fileWriteOutOfSpace)
                }
                try data.write(to: url)
            }
        )
        let note = Note()
        note.title = "Keep me"
        XCTAssertTrue(store.persistNewNote(note))
        shouldFailWrite = true

        XCTAssertFalse(store.deleteNote(0))
        XCTAssertEqual(store.count(), 1)
        XCTAssertTrue(store.getNote(0) === note)
    }

    func testSecondCorruptArchivePreservesEarlierQuarantine() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        let earlierCorruption = Data("earlier corruption".utf8)
        let laterCorruption = Data("later corruption".utf8)
        try earlierCorruption.write(to: urls.quarantine)
        try laterCorruption.write(to: urls.archive)

        _ = NoteStore(archiveURL: urls.archive)

        XCTAssertEqual(try Data(contentsOf: urls.quarantine), earlierCorruption)
        let quarantines = try FileManager.default.contentsOfDirectory(
            at: urls.directory,
            includingPropertiesForKeys: nil
        ).filter { $0.lastPathComponent.hasPrefix("NoteStore.corrupt-") }
        XCTAssertEqual(quarantines.count, 1)
        XCTAssertEqual(try Data(contentsOf: quarantines[0]), laterCorruption)
    }

    func testOversizedArchiveIsRejectedBeforeReading() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        try Data(repeating: 0x41, count: NoteStore.maximumArchiveBytes + 1).write(to: urls.archive)
        var loaderWasCalled = false

        let store = NoteStore(archiveURL: urls.archive) { _ in
            loaderWasCalled = true
            return Data()
        }

        XCTAssertFalse(loaderWasCalled)
        XCTAssertEqual(store.count(), 0)
        XCTAssertFalse(FileManager.default.fileExists(atPath: urls.archive.path))
    }

    func testArchiveSymlinkIsNeverFollowedOrReplaced() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        let target = urls.directory.appendingPathComponent("outside.plist")
        let protectedData = Data("do not touch".utf8)
        try protectedData.write(to: target)
        try FileManager.default.createSymbolicLink(at: urls.archive, withDestinationURL: target)

        let store = NoteStore(archiveURL: urls.archive)
        _ = store.createNote()

        XCTAssertEqual(try Data(contentsOf: target), protectedData)
        XCTAssertEqual(
            try FileManager.default.destinationOfSymbolicLink(atPath: urls.archive.path),
            target.path
        )
    }

    func testFailedPersistenceIsReportedAndLeavesPreviousArchiveUntouched() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        let originalData = Data("existing archive".utf8)
        try originalData.write(to: urls.archive)
        let store = NoteStore(
            archiveURL: urls.archive,
            archiveDataLoader: { _ in throw CocoaError(.fileReadNoPermission) },
            archiveDataWriter: { _, _ in throw CocoaError(.fileWriteOutOfSpace) }
        )

        XCTAssertFalse(store.save())
        XCTAssertEqual(try Data(contentsOf: urls.archive), originalData)
    }

    func testDecodedArchiveRejectsExcessiveNoteCount() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        let notes = (0...NoteStore.maximumNoteCount).map { _ in Note() }
        let data = try NSKeyedArchiver.archivedData(
            withRootObject: notes,
            requiringSecureCoding: true
        )
        try data.write(to: urls.archive)

        let store = NoteStore(archiveURL: urls.archive)

        XCTAssertEqual(store.count(), 0)
        XCTAssertFalse(FileManager.default.fileExists(atPath: urls.archive.path))
    }

    func testNoteTextAndTitleRemoveControlsAndEnforceBounds() {
        let longTitle = "\u{202E}" + String(repeating: "a", count: Note.maximumTitleLength + 20)
        let longText = "safe\u{0000}text" + String(repeating: "b", count: Note.maximumTextLength)

        let title = Note.normalizedTitle(longTitle)
        let text = Note.normalizedText(longText)

        XCTAssertFalse(title.unicodeScalars.contains { CharacterSet.controlCharacters.contains($0) })
        XCTAssertFalse(title.unicodeScalars.contains { CharacterSet(charactersIn: "\u{202A}"..."\u{202E}").contains($0) })
        XCTAssertLessThanOrEqual(title.count, Note.maximumTitleLength)
        XCTAssertFalse(text.unicodeScalars.contains { CharacterSet.controlCharacters.contains($0) && $0 != "\n" && $0 != "\t" })
        XCTAssertLessThanOrEqual(text.count, Note.maximumTextLength)
    }

    func testStoreFindsExistingNoteByIdentity() throws {
        let urls = try temporaryArchiveURLs()
        defer { try? FileManager.default.removeItem(at: urls.directory) }
        let store = NoteStore(archiveURL: urls.archive)
        let existing = store.createNote(Note())

        XCTAssertEqual(store.index(of: existing), 0)
        XCTAssertNil(store.index(of: Note()))
    }

}
