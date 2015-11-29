//
//  NotesTableViewController.swift


import UIKit

class TableViewController: UITableViewController {

    var logoView: UIImageView!

    override func viewDidLoad() {
        super.viewDidLoad()

        self.setupNav()

        // Leverage the built in TableViewController Edit button
        self.navigationItem.leftBarButtonItem = self.editButtonItem()
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

    override func viewWillAppear(animated: Bool) {
        super.viewWillAppear(animated)
        // ensure we are not in edit mode
        editing = false
    }

    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject?) {
        // Here we pass the note they tapped on between the view controllers
        if segue.identifier == "NoteDetailPush" {
            // Get the controller we are going to
            let noteDetail = segue.destinationViewController as! DetailViewController
            // Lookup the data we want to pass
            let theCell = sender as! DetailTableViewCell
            // Pass the data forward
            noteDetail.theNote = theCell.theNote
        }
    }


    @IBAction func saveFromNoteDetail(segue:UIStoryboardSegue) {
        // We come here from an exit segue when they hit save on the detail screen

        // Get the controller we are coming from
        let noteDetail = segue.sourceViewController as! DetailViewController

        // If there is a row selected....
        if let indexPath = tableView.indexPathForSelectedRow {
            // Update note in our store
            NoteStore.sharedNoteStore.updateNote(theNote: noteDetail.theNote)

            // The user was in edit mode
            tableView.reloadRowsAtIndexPaths([indexPath], withRowAnimation: UITableViewRowAnimation.Automatic)
        } else {
            // Otherwise, add a new record
            NoteStore.sharedNoteStore.createNote(noteDetail.theNote)

            // Get an index to insert the row at
            let indexPath = NSIndexPath(forRow: NoteStore.sharedNoteStore.count()-1, inSection: 0)

            // Update tableview
            tableView.insertRowsAtIndexPaths([indexPath], withRowAnimation: UITableViewRowAnimation.Automatic)
        }
    }

    // MARK: - Table view data source

    override func tableView(tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        // Just return the note count
        return NoteStore.sharedNoteStore.count()
    }


    override func tableView(tableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        // Fetch a reusable cell
        let cell = tableView.dequeueReusableCellWithIdentifier("DetailTableViewCell", forIndexPath: indexPath) as! DetailTableViewCell

        // Fetch the note
        let rowNumber = indexPath.row
        let theNote = NoteStore.sharedNoteStore.getNote(rowNumber)

        // Configure the cell
        cell.setupCell(theNote)

        return cell
    }


    // Override to support editing the table view.
    override func tableView(tableView: UITableView, commitEditingStyle editingStyle: UITableViewCellEditingStyle, forRowAtIndexPath indexPath: NSIndexPath) {

        if editingStyle == .Delete {
            // Delete the row from the data source
            NoteStore.sharedNoteStore.deleteNote(indexPath.row)
            // Delete the note from the tableview
            tableView.deleteRowsAtIndexPaths([indexPath], withRowAnimation: .Fade)
        }
    }


}
