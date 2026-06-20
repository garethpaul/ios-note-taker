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

        let store = NoteStore.sharedNoteStore
        let input = noteDetail.normalizedInput()
        if let row = store.index(of: noteDetail.theNote) {
            guard store.persistChanges(to: noteDetail.theNote, title: input.title, text: input.text) else {
                presentPersistenceFailure()
                return
            }
            tableView.reloadRows(at: [IndexPath(row: row, section: 0)], with: .automatic)
        } else {
            noteDetail.theNote.title = input.title
            noteDetail.theNote.text = input.text
            guard store.persistNewNote(noteDetail.theNote) else {
                presentPersistenceFailure()
                return
            }
            let indexPath = IndexPath(row: store.count() - 1, section: 0)
            tableView.insertRows(at: [indexPath], with: .automatic)
        }
    }

    private func presentPersistenceFailure() {
        let alert = UIAlertController(
            title: "Note Not Saved",
            message: "The note archive could not be updated. Your previous saved notes were left unchanged.",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
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
