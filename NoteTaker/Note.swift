//
//  Note.swift
//

import Foundation

// MARK: Note model for storing the note.
class Note: NSObject, NSSecureCoding {
    static var supportsSecureCoding: Bool { true }

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
        let trimmedTitle = (title ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmedTitle.isEmpty ? "Untitled" : trimmedTitle
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
        self.text = coder.decodeObject(of: NSString.self, forKey: "text") as? String ?? ""
        self.date = coder.decodeObject(of: NSDate.self, forKey: "date") as? Date ?? Date()
        super.init()
    }

}
