//
//  NoteStore.swift
//

import Foundation

class NoteStore {
    static let sharedNoteStore = NoteStore()

    private let archiveURL: URL?
    private let archiveDataLoader: (URL) throws -> Data
    private var archiveWritesBlocked = false

    // Private init to force usage of singleton
    private init() {
        archiveURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)
            .first?
            .appendingPathComponent("NoteStore.plist")
        archiveDataLoader = { try Data(contentsOf: $0) }
        load()
    }

    init(archiveURL: URL?, archiveDataLoader: @escaping (URL) throws -> Data = { try Data(contentsOf: $0) }) {
        self.archiveURL = archiveURL
        self.archiveDataLoader = archiveDataLoader
        load()
    }

    // Array to hold our notes
    private var notes = [Note]()

    // CRUD - Create, Read, Update, Delete

    // Create

    func createNote(_ theNote: Note = Note()) -> Note {
        notes.append(theNote)
        save()
        return theNote
    }

    // Read

    func getNote(_ index: Int) -> Note? {
        if index < 0 || index >= notes.count {
            return nil
        }

        return notes[index]
    }

    // Update
    func updateNote(theNote: Note) {
        // Notes passed by reference, no update code needed
        save()
    }

    // Delete
    func deleteNote(_ index: Int) -> Bool {
        if index < 0 || index >= notes.count {
            return false
        }
        notes.remove(at: index)
        save()
        return true
    }

    func deleteNote(_ withNote: Note) -> Bool {

        for (i, note) in notes.enumerated() {
            if note === withNote {
                notes.remove(at: i)
                save()
                return true
            }
        }

        return false

    }

    // Count
    func count() -> Int {
        return notes.count
    }


    // Mark: Persistence

    // 1: Find the file & directory we want to save to...
    func archiveFileURL() -> URL? {
        return archiveURL
    }

    // 2: Do the save to disk.....
    func save() {
        guard !archiveWritesBlocked else {
            return
        }
        guard let url = archiveFileURL() else {
            return
        }
        do {
            let data = try NSKeyedArchiver.archivedData(withRootObject: notes, requiringSecureCoding: true)
            try data.write(to: url, options: [.atomic, .completeFileProtection])
            applyFileProtection(url.path)
        } catch {
            // Keep the in-memory notes available when local persistence fails.
        }
    }

    func applyFileProtection(_ path: String) {
        do {
            let attributes: [FileAttributeKey: Any] = [.protectionKey: FileProtectionType.complete]
            try FileManager.default.setAttributes(attributes, ofItemAtPath: path)
        } catch {
            // Keep local note saves available when protection attributes cannot be set.
        }
    }

    private func corruptArchiveFileURL(_ archiveURL: URL) -> URL {
        return archiveURL.deletingLastPathComponent()
            .appendingPathComponent("NoteStore.corrupt.plist")
    }

    private func quarantineCorruptArchive(_ archiveURL: URL) -> Bool {
        let fileManager = FileManager.default
        let quarantineURL = corruptArchiveFileURL(archiveURL)

        do {
            if fileManager.fileExists(atPath: quarantineURL.path) {
                try fileManager.removeItem(at: quarantineURL)
            }
            try fileManager.moveItem(at: archiveURL, to: quarantineURL)
            applyFileProtection(quarantineURL.path)
            return true
        } catch {
            // Keep note content and local paths out of logs when quarantine fails.
            return false
        }
    }


    // 3: Do the reload from disk....
    func load() {
        guard let fileURL = archiveFileURL() else {
            notes = []
            return
        }

        let archiveExists = FileManager.default.fileExists(atPath: fileURL.path)
        let data: Data
        do {
            data = try archiveDataLoader(fileURL)
        } catch {
            notes = []
            archiveWritesBlocked = archiveExists
            return
        }

        do {
            let allowedClasses: [AnyClass] = [NSArray.self, Note.self, NSString.self, NSDate.self]
            guard let decodedNotes = try NSKeyedUnarchiver.unarchivedObject(
                ofClasses: allowedClasses,
                from: data
            ) as? [Note] else {
                notes = []
                archiveWritesBlocked = !quarantineCorruptArchive(fileURL)
                return
            }
            notes = decodedNotes
            archiveWritesBlocked = false
        } catch {
            notes = []
            archiveWritesBlocked = !quarantineCorruptArchive(fileURL)
        }
    }
    
}
