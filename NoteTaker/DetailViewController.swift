//
//  DetailViewController.swift


import UIKit

class DetailViewController: UIViewController {

    var theNote = Note()
    var logoView: UIImageView!

    // MARK: IBOutlet
    @IBOutlet weak var noteTitleLabel: UITextField!
    @IBOutlet weak var noteTextView: UITextView!

    override func viewDidLoad() {
        super.viewDidLoad()

        // The view starts here. By now we either have a note to edit
        // or we have a blank note in theNote property we can use

        // Update the screen with the contents of theNote
        self.noteTitleLabel.text = theNote.title
        self.noteTextView.text = theNote.text

        // Set the Cursor in the note text area
        self.noteTextView.becomeFirstResponder()

        self.setupNav()
        
    }

    // MARK: Nav Helper
    func setupNav() {
        // Setup Image
        logoView = UIImageView(frame: CGRect(x: 0, y: 0, width: 30, height: 30))
        logoView.image = UIImage(named: "miniLogo")?.withRenderingMode(.alwaysTemplate)
        logoView.tintColor = toColor("#6F6664")
        self.navigationItem.titleView = logoView
    }


    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Whenever we leave the screen, update our note model
        theNote.title = Note.normalizedTitle(self.noteTitleLabel.text)
        theNote.text = self.noteTextView.text ?? ""
    }

}
