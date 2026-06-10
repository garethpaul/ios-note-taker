//
//  NotesTableViewController.swift


import UIKit

class TableViewController: UITableViewController {

    var logoView: UIImageView!

    override func viewDidLoad() {
        super.viewDidLoad()
        self.setupNav()
        // Leverage the built in TableViewController Edit button
        self.navigationItem.leftBarButtonItem = self.editButtonItem
    }

    func setupNav() {
        logoView = UIImageView(frame: CGRect(x: 0, y: 0, width: 30, height: 30))
        logoView.image = UIImage(named: "miniLogo")?.withRenderingMode(.alwaysTemplate)
        logoView.tintColor = toColor("#6F6664")
        self.navigationItem.titleView = logoView
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        // ensure we are not in edit mode
        isEditing = false
    }

    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Here we pass the note they tapped on between the view controllers
        if segue.identifier == "NoteDetailPush" {
            // Get the controller we are going to
            guard let noteDetail = segue.destination as? DetailViewController else {
                return
            }
            // Lookup the data we want to pass
            guard let theCell = sender as? DetailTableViewCell,
                let theNote = theCell.theNote else {
                    return
            }
            // Pass the data forward
            noteDetail.theNote = theNote
        }
    }

    // MARK: IBActions
    @IBAction func saveFromNoteDetail(_ segue: UIStoryboardSegue) {
        // We come here from an exit segue when they hit save on the detail screen

        // Get the controller we are coming from
        guard let noteDetail = segue.source as? DetailViewController else {
            return
        }

        // If there is a row selected....
        if let indexPath = tableView.indexPathForSelectedRow {
            // Update note in our store
            NoteStore.sharedNoteStore.updateNote(theNote: noteDetail.theNote)

            // The user was in edit mode
            tableView.reloadRows(at: [indexPath], with: .automatic)
        } else {
            // Otherwise, add a new record
            _ = NoteStore.sharedNoteStore.createNote(noteDetail.theNote)

            // Get an index to insert the row at
            let indexPath = IndexPath(row: NoteStore.sharedNoteStore.count() - 1, section: 0)

            // Update tableview
            tableView.insertRows(at: [indexPath], with: .automatic)
        }
    }

    // MARK: - Table view data source

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        // Just return the note count
        return NoteStore.sharedNoteStore.count()
    }


    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        // Fetch a reusable cell
        guard let cell = tableView.dequeueReusableCell(withIdentifier: "DetailTableViewCell", for: indexPath) as? DetailTableViewCell else {
            return UITableViewCell()
        }

        // Fetch the note
        let rowNumber = indexPath.row
        guard let theNote = NoteStore.sharedNoteStore.getNote(rowNumber) else {
            return cell
        }

        // Configure the cell
        cell.setupCell(theNote)

        return cell
    }


    // Override to support editing the table view.
    override func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCell.EditingStyle, forRowAt indexPath: IndexPath) {

        if editingStyle == .delete {
            // Delete the row from the data source
            if NoteStore.sharedNoteStore.deleteNote(indexPath.row) {
                // Delete the note from the tableview
                tableView.deleteRows(at: [indexPath], with: .fade)
            }
        }
    }


}
