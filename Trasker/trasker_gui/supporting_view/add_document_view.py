import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import mimetypes

class AddDocumentView(tk.Toplevel):
    def __init__(self, parent, controller, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.refresh_callback = refresh_callback
        self.title("Add Document")
        self.geometry("600x500")

        # This variable will hold the selected note id.
        self.note_id = None

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # File selection section
        ttk.Label(frame, text="Select Document:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.file_label = ttk.Label(frame, text="No file selected")
        self.file_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)

        # Note search and selection section
        ttk.Label(frame, text="Search for Note:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(frame, textvariable=self.search_var)
        self.search_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5, columnspan=2)
        self.search_entry.bind("<KeyRelease>", self.filter_notes)

        ttk.Label(frame, text="Select Note:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.note_combo = ttk.Combobox(frame, state="readonly")
        self.note_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5, columnspan=2)
        frame.columnconfigure(1, weight=1)
        self.load_notes()

        # Button to add document
        ttk.Button(frame, text="Add Document", command=self.add_document).grid(row=3, column=0, columnspan=3, pady=10)

        self.selected_file = None

    def browse_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.selected_file = filepath
            self.file_label.config(text=os.path.basename(filepath))

    def load_notes(self):
        """Load all notes from the database into the combobox and map display text to note IDs."""
        notes = self.controller.trasker.list_notes()  # Expected to return a list of tuples (id, note, note_type, …)
        self.all_notes = []
        self.note_map = {}
        for note in notes:
            note_id = note[0]
            note_text = note[1]
            note_type = note[2]  # Using note_type for display
            display_text = f"ID {note_id} [{note_type}]: {note_text[:30]}{'...' if len(note_text) > 30 else ''}"
            self.all_notes.append(display_text)
            self.note_map[display_text] = note_id
        self.note_combo['values'] = self.all_notes
        if self.all_notes:
            self.note_combo.current(0)
            self.note_id = self.note_map[self.all_notes[0]]
        else:
            self.note_id = None
        self.note_combo.bind("<<ComboboxSelected>>", self.on_note_selected)

    def on_note_selected(self, event):
        selection = self.note_combo.get()
        self.note_id = self.note_map.get(selection)

    def filter_notes(self, event):
        """Filter notes based on the search text."""
        search_text = self.search_var.get().lower()
        filtered = [d for d in self.all_notes if search_text in d.lower()]
        self.note_combo['values'] = filtered
        if filtered:
            self.note_combo.current(0)
            self.note_id = self.note_map[filtered[0]]
        else:
            self.note_id = None

    def add_document(self):
        if not self.selected_file:
            messagebox.showerror("Error", "No file selected!")
            return
        # Allow adding a document without linking to a note.
        if not self.note_id:
            if not messagebox.askyesno("No Note Selected", "No note is selected. Do you want to add the document without linking to a note?"):
                return

        filename = os.path.basename(self.selected_file)
        mimetype, _ = mimetypes.guess_type(self.selected_file)
        mimetype = mimetype or "application/octet-stream"

        try:
            with open(self.selected_file, "rb") as f:
                document_blob = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")
            return

        # Retrieve current user and team from the controller's Trasker instance.
        current_user = self.controller.trasker.current_user
        if isinstance(current_user, tuple):
            user_id = current_user[0]
        else:
            user_id = current_user

        current_team = self.controller.trasker.current_team
        if isinstance(current_team, tuple):
            team_id = current_team[0]
        else:
            team_id = current_team

        try:
            # Call the Trasker method to add the document with user and team association.
            self.controller.trasker.add_document(self.note_id, filename, mimetype, document_blob, user_id, team_id)
            messagebox.showinfo("Success", "Document added successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add document: {e}")
            return

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
