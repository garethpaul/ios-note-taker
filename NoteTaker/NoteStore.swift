//
//  NoteStore.swift
//

import Foundation

class NoteStore {
    // Mark: Singleton Pattern (hacked since we don't have class var's yet)
    class var sharedNoteStore : NoteStore {
        struct Static {
            static let instance : NoteStore = NoteStore()
        }
        return Static.instance
    }

    // Private init to force usage of singleton
    private init() {
        load()
    }

    // Array to hold our notes
    private var notes : [Note]!

    // CRUD - Create, Read, Update, Delete

    // Create

    func createNote(theNote:Note = Note()) -> Note {
        notes.append(theNote)
        save()
        return theNote
    }

    // Read

    func getNote(index:Int) -> Note {
        return notes[index]
    }

    // Update
    func updateNote(theNote theNote:Note) {
        // Notes passed by reference, no update code needed
        save()
    }

    // Delete
    func deleteNote(index:Int) {
        if index < 0 || index >= notes.count {
            return
        }
        notes.removeAtIndex(index)
        save()
    }

    func deleteNote(withNote:Note) {

        for (i, note) in notes.enumerate() {
            if note === withNote {
                notes.removeAtIndex(i)
                save()
                return
            }
        }

    }

    // Count
    func count() -> Int {
        return notes.count
    }


    // Mark: Persistence

    // 1: Find the file & directory we want to save to...
    func archiveFilePath() -> String? {
        let paths = NSSearchPathForDirectoriesInDomains(.DocumentDirectory, .UserDomainMask, true)
        guard let firstPath = paths.first else {
            return nil
        }
        let documentsDirectory = firstPath as NSString
        let path = documentsDirectory.stringByAppendingPathComponent("NoteStore.plist")

        return path
    }

    // 2: Do the save to disk.....
    func save() {
        guard let path = archiveFilePath() else {
            return
        }
        let archived = NSKeyedArchiver.archiveRootObject(notes, toFile: path)
        if archived {
            applyFileProtection(path)
        }
    }

    func applyFileProtection(path:String) {
        do {
            let attributes: [String: AnyObject] = [NSFileProtectionKey: NSFileProtectionComplete]
            try NSFileManager.defaultManager().setAttributes(attributes, ofItemAtPath: path)
        } catch {
            // Keep local note saves available when protection attributes cannot be set.
        }
    }


    // 3: Do the reload from disk....
    func load() {
        guard let filePath = archiveFilePath() else {
            notes = [Note]()
            return
        }
        let fileManager = NSFileManager.defaultManager()

        if fileManager.fileExistsAtPath(filePath) {
            if let archivedNotes = NSKeyedUnarchiver.unarchiveObjectWithFile(filePath) as? [Note] {
                notes = archivedNotes
            } else {
                notes = [Note]()
            }
        } else {
            notes = [Note]()
        }
    }
    
}
