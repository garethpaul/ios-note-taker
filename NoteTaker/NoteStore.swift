//
//  NoteStore.swift
//

import Darwin
import Foundation

class NoteStore {
    static let sharedNoteStore = NoteStore()
    static let maximumArchiveBytes = 5 * 1024 * 1024
    static let maximumNoteCount = 1_000

    private let archiveURL: URL?
    private let archiveDataLoader: (URL) throws -> Data
    private let archiveDataWriter: (Data, URL) throws -> Void
    private var archiveWritesBlocked = false

    private init() {
        archiveURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)
            .first?
            .appendingPathComponent("NoteStore.plist")
        archiveDataLoader = { try Data(contentsOf: $0, options: [.mappedIfSafe]) }
        archiveDataWriter = { try NoteStore.writeProtectedArchive($0, to: $1) }
        load()
    }

    init(
        archiveURL: URL?,
        archiveDataLoader: @escaping (URL) throws -> Data = { try Data(contentsOf: $0, options: [.mappedIfSafe]) },
        archiveDataWriter: @escaping (Data, URL) throws -> Void = { try NoteStore.writeProtectedArchive($0, to: $1) }
    ) {
        self.archiveURL = archiveURL
        self.archiveDataLoader = archiveDataLoader
        self.archiveDataWriter = archiveDataWriter
        load()
    }

    private var notes = [Note]()

    func createNote(_ note: Note = Note()) -> Note {
        notes.append(note)
        _ = save()
        return note
    }

    func persistNewNote(_ note: Note) -> Bool {
        guard notes.count < NoteStore.maximumNoteCount else {
            return false
        }
        note.normalizeStoredContent()
        notes.append(note)
        guard save() else {
            notes.removeLast()
            return false
        }
        return true
    }

    func getNote(_ index: Int) -> Note? {
        guard notes.indices.contains(index) else {
            return nil
        }
        return notes[index]
    }

    func index(of note: Note) -> Int? {
        return notes.firstIndex { $0 === note }
    }

    @discardableResult
    func updateNote(theNote: Note) -> Bool {
        guard index(of: theNote) != nil else {
            return false
        }
        theNote.normalizeStoredContent()
        return save()
    }

    func persistChanges(to note: Note, title: String?, text: String?) -> Bool {
        guard index(of: note) != nil else {
            return false
        }
        let previousTitle = note.title
        let previousText = note.text
        note.title = Note.normalizedTitle(title)
        note.text = Note.normalizedText(text)
        guard save() else {
            note.title = previousTitle
            note.text = previousText
            return false
        }
        return true
    }

    func deleteNote(_ index: Int) -> Bool {
        guard notes.indices.contains(index) else {
            return false
        }
        let removedNote = notes.remove(at: index)
        guard save() else {
            notes.insert(removedNote, at: index)
            return false
        }
        return true
    }

    func deleteNote(_ note: Note) -> Bool {
        guard let index = index(of: note) else {
            return false
        }
        return deleteNote(index)
    }

    func count() -> Int {
        return notes.count
    }

    func archiveFileURL() -> URL? {
        return archiveURL
    }

    @discardableResult
    func save() -> Bool {
        guard !archiveWritesBlocked, let url = archiveFileURL(), archiveURLIsSafeForWriting(url) else {
            return false
        }
        guard notes.count <= NoteStore.maximumNoteCount else {
            return false
        }

        notes.forEach { $0.normalizeStoredContent() }
        do {
            let data = try NSKeyedArchiver.archivedData(withRootObject: notes, requiringSecureCoding: true)
            guard data.count <= NoteStore.maximumArchiveBytes else {
                return false
            }
            try archiveDataWriter(data, url)
            return true
        } catch {
            return false
        }
    }

    private func archiveURLIsSafeForWriting(_ url: URL) -> Bool {
        guard url.isFileURL, url.standardizedFileURL.path == url.path else {
            return false
        }
        let parent = url.deletingLastPathComponent()
        guard let parentValues = try? parent.resourceValues(forKeys: [.isDirectoryKey, .isSymbolicLinkKey]),
              parentValues.isDirectory == true,
              parentValues.isSymbolicLink != true else {
            return false
        }
        guard FileManager.default.fileExists(atPath: url.path) else {
            return true
        }
        guard let values = try? url.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey]) else {
            return false
        }
        return values.isRegularFile == true && values.isSymbolicLink != true
    }

    private func corruptArchiveFileURL(_ archiveURL: URL) -> URL {
        let directory = archiveURL.deletingLastPathComponent()
        let preferredURL = directory.appendingPathComponent("NoteStore.corrupt.plist")
        if !FileManager.default.fileExists(atPath: preferredURL.path) {
            return preferredURL
        }
        return directory.appendingPathComponent("NoteStore.corrupt-\(UUID().uuidString).plist")
    }

    private func quarantineCorruptArchive(_ archiveURL: URL) -> Bool {
        guard archiveURLIsSafeForWriting(archiveURL) else {
            return false
        }
        let quarantineURL = corruptArchiveFileURL(archiveURL)
        do {
            try FileManager.default.moveItem(at: archiveURL, to: quarantineURL)
            try NoteStore.applyFileProtection(to: quarantineURL)
            try NoteStore.synchronizeDirectory(quarantineURL.deletingLastPathComponent())
            return true
        } catch {
            return false
        }
    }

    func load() {
        guard let fileURL = archiveFileURL() else {
            notes = []
            archiveWritesBlocked = true
            return
        }

        guard fileURL.isFileURL, fileURL.standardizedFileURL.path == fileURL.path else {
            notes = []
            archiveWritesBlocked = true
            return
        }

        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            notes = []
            archiveWritesBlocked = false
            return
        }

        guard let values = try? fileURL.resourceValues(forKeys: [.fileSizeKey, .isRegularFileKey, .isSymbolicLinkKey]),
              values.isRegularFile == true,
              values.isSymbolicLink != true else {
            notes = []
            archiveWritesBlocked = true
            return
        }

        if (values.fileSize ?? NoteStore.maximumArchiveBytes + 1) > NoteStore.maximumArchiveBytes {
            notes = []
            archiveWritesBlocked = !quarantineCorruptArchive(fileURL)
            return
        }

        let data: Data
        do {
            data = try archiveDataLoader(fileURL)
        } catch {
            notes = []
            archiveWritesBlocked = true
            return
        }

        guard data.count <= NoteStore.maximumArchiveBytes else {
            notes = []
            archiveWritesBlocked = !quarantineCorruptArchive(fileURL)
            return
        }

        do {
            let allowedClasses: [AnyClass] = [NSArray.self, Note.self, NSString.self, NSDate.self]
            guard let decodedNotes = try NSKeyedUnarchiver.unarchivedObject(
                ofClasses: allowedClasses,
                from: data
            ) as? [Note], decodedNotes.count <= NoteStore.maximumNoteCount else {
                notes = []
                archiveWritesBlocked = !quarantineCorruptArchive(fileURL)
                return
            }
            decodedNotes.forEach { $0.normalizeStoredContent() }
            notes = decodedNotes
            archiveWritesBlocked = false
        } catch {
            notes = []
            archiveWritesBlocked = !quarantineCorruptArchive(fileURL)
        }
    }

    private static func writeProtectedArchive(_ data: Data, to destinationURL: URL) throws {
        let directoryURL = destinationURL.deletingLastPathComponent()
        let temporaryURL = directoryURL.appendingPathComponent(".NoteStore-\(UUID().uuidString).tmp")
        let descriptor = open(temporaryURL.path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, S_IRUSR | S_IWUSR)
        guard descriptor >= 0 else {
            throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
        }

        var shouldRemoveTemporaryFile = true
        defer {
            close(descriptor)
            if shouldRemoveTemporaryFile {
                try? FileManager.default.removeItem(at: temporaryURL)
            }
        }

        try data.withUnsafeBytes { rawBuffer in
            guard var baseAddress = rawBuffer.baseAddress else {
                return
            }
            var bytesRemaining = rawBuffer.count
            while bytesRemaining > 0 {
                let written = Darwin.write(descriptor, baseAddress, bytesRemaining)
                if written < 0 {
                    if errno == EINTR { continue }
                    throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
                }
                bytesRemaining -= written
                baseAddress = baseAddress.advanced(by: written)
            }
        }

        guard fchmod(descriptor, S_IRUSR | S_IWUSR) == 0 else {
            throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
        }
        try applyFileProtection(to: temporaryURL)
        guard fsync(descriptor) == 0 else {
            throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
        }
        guard rename(temporaryURL.path, destinationURL.path) == 0 else {
            throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
        }
        shouldRemoveTemporaryFile = false
        try synchronizeDirectory(directoryURL)
    }

    private static func applyFileProtection(to url: URL) throws {
        let attributes: [FileAttributeKey: Any] = [
            .protectionKey: FileProtectionType.complete,
            .posixPermissions: 0o600
        ]
        try FileManager.default.setAttributes(attributes, ofItemAtPath: url.path)
    }

    private static func synchronizeDirectory(_ directoryURL: URL) throws {
        let descriptor = open(directoryURL.path, O_RDONLY | O_DIRECTORY)
        guard descriptor >= 0 else {
            throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
        }
        defer { close(descriptor) }
        guard fsync(descriptor) == 0 else {
            throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
        }
    }
}
