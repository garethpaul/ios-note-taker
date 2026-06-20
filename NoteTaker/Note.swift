//
//  Note.swift
//

import Foundation

// MARK: Note model for storing the note.
class Note: NSObject, NSSecureCoding {
    static var supportsSecureCoding: Bool { true }
    static let maximumTitleLength = 120
    static let maximumTextLength = 100_000

    var title = ""
    var text = ""
    var date = Date() // Defaults to current date / time

    // Computed property to return date as a string
    var shortDate: String {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "MM/dd/yy"
        return dateFormatter.string(from: self.date)
    }

    override init() {
        super.init()
    }

    class func normalizedTitle(_ title: String?) -> String {
        let trimmedTitle = sanitizedText(title ?? "", allowNewlines: false, maximumLength: maximumTitleLength)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmedTitle.isEmpty ? "Untitled" : trimmedTitle
    }

    class func normalizedText(_ text: String?) -> String {
        return sanitizedText(text ?? "", allowNewlines: true, maximumLength: maximumTextLength)
    }

    func normalizeStoredContent() {
        title = Note.normalizedTitle(title)
        text = Note.normalizedText(text)
    }

    private class func sanitizedText(_ text: String, allowNewlines: Bool, maximumLength: Int) -> String {
        let bidiControls = CharacterSet(charactersIn: "\u{061C}\u{200E}\u{200F}\u{202A}\u{202B}\u{202C}\u{202D}\u{202E}\u{2066}\u{2067}\u{2068}\u{2069}")
        let filteredScalars = text.unicodeScalars.filter { scalar in
            if bidiControls.contains(scalar) || CharacterSet.illegalCharacters.contains(scalar) {
                return false
            }
            if CharacterSet.controlCharacters.contains(scalar) {
                return allowNewlines && (scalar == "\n" || scalar == "\t")
            }
            return true
        }
        return String(String.UnicodeScalarView(filteredScalars)).prefix(maximumLength).description
    }

    // 1: Encode ourselves...
    func encode(with coder: NSCoder) {
        coder.encode(title, forKey: "title")
        coder.encode(text, forKey: "text")
        coder.encode(date, forKey: "date")
    }

    // 2: Decode ourselves on init
    required init?(coder: NSCoder) {
        self.title = Note.normalizedTitle(coder.decodeObject(of: NSString.self, forKey: "title") as? String)
        self.text = Note.normalizedText(coder.decodeObject(of: NSString.self, forKey: "text") as? String)
        self.date = coder.decodeObject(of: NSDate.self, forKey: "date") as? Date ?? Date()
        super.init()
    }

}
