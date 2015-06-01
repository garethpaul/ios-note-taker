//
//  DetailViewController.swift


import UIKit

class DetailViewController: UIViewController {

    var theNote = Note()

    var logoView: UIImageView!

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

    func setupNav() {
        logoView = UIImageView(frame: CGRectMake(0, 0, 30, 30))
        logoView.image = UIImage(named: "miniLogo")?.imageWithRenderingMode(.AlwaysTemplate)
        logoView.frame.origin.x = (self.view.frame.size.width - logoView.frame.size.width) / 2
        logoView.frame.origin.y = 25
        logoView.tintColor = toColor("#6F6664")

        // Add to subview
        self.navigationController?.view.addSubview(logoView)

        // Bring the logo view to the front.
        self.navigationController?.view.bringSubviewToFront(logoView)
    }


    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject?) {
        // Whenever we leave the screen, update our note model
        theNote.title = self.noteTitleLabel.text
        theNote.text = self.noteTextView.text
    }

}
