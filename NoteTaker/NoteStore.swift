//
//  NoteStore.swift
//

import Foundation

class NoteStore {
    static let sharedNoteStore = NoteStore()

    // Private init to force usage of singleton
    private init() {
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
        return FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)
            .first?
            .appendingPathComponent("NoteStore.plist")
    }

    // 2: Do the save to disk.....
    func save() {
        guard let url = archiveFileURL() else {
            return
        }
        do {
            let data = try NSKeyedArchiver.archivedData(withRootObject: notes, requiringSecureCoding: true)
            try data.write(to: url, options: .atomic)
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


    // 3: Do the reload from disk....
    func load() {
        guard let fileURL = archiveFileURL() else {
            notes = []
            return
        }

        do {
            let data = try Data(contentsOf: fileURL)
            let allowedClasses: [AnyClass] = [NSArray.self, Note.self, NSString.self, NSDate.self]
            notes = try NSKeyedUnarchiver.unarchivedObject(ofClasses: allowedClasses, from: data) as? [Note] ?? []
        } catch {
            notes = []
        }
    }
    
}
