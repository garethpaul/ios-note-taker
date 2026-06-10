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

    func testNoteTitleNormalizationTrimsWhitespace() {
        XCTAssertEqual(Note.normalizedTitle("  Groceries\n"), "Groceries", "Note titles should be trimmed before saving")
    }

    func testNoteTitleNormalizationDefaultsBlankTitles() {
        XCTAssertEqual(Note.normalizedTitle("  \n\t  "), "Untitled", "Blank note titles should use the visible fallback")
        XCTAssertEqual(Note.normalizedTitle(nil), "Untitled", "Missing note titles should use the visible fallback")
    }

    func testDecodedBlankTitleUsesVisibleFallback() {
        let data = NSMutableData()
        let archiver = NSKeyedArchiver(forWritingWithMutableData: data)
        archiver.encodeObject("  \n\t  ", forKey: "title")
        archiver.encodeObject("body", forKey: "text")
        archiver.encodeObject(NSDate(), forKey: "date")
        archiver.finishEncoding()

        let unarchiver = NSKeyedUnarchiver(forReadingWithData: data)
        let note = Note(coder: unarchiver)

        XCTAssertEqual(note!.title, "Untitled", "Archived blank note titles should use the visible fallback")
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
