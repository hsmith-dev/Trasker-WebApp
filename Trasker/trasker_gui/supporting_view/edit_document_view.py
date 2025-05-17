import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import mimetypes

class EditDocumentView(tk.Toplevel):
    def __init__(self, parent, controller, document_id, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.document_id = document_id
        self.refresh_callback = refresh_callback
        self.title("Edit Document")
        self.geometry("600x400")

        # Retrieve the document details from the database.
        # Expecting the document tuple to be:
        # (id, note_id, filename, mimetype, document_blob, upload_date, user_id, team_id)
        document = self.controller.trasker.get_document(self.document_id)
        if not document:
            messagebox.showerror("Error", "Document not found!")
            self.destroy()
            return

        # Unpack the document tuple. We ignore any extra fields (user_id, team_id) by using *_
        doc_id, self.note_id, filename, mimetype, document_blob, upload_date, *_ = document

        # Build the UI.
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Current Filename:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=filename).grid(
            row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Select New Document:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        self.file_label = ttk.Label(frame, text="No file selected")
        self.file_label.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_file).grid(
            row=1, column=2, padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Save Changes", command=self.save_changes).grid(
            row=2, column=0, columnspan=3, pady=10)

        self.selected_file = None

    def browse_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.selected_file = filepath
            self.file_label.config(text=os.path.basename(filepath))

    def save_changes(self):
        if not self.selected_file:
            messagebox.showerror("Error", "No new file selected!")
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

        # Update the document record in the database.
        self.controller.trasker.update_document(self.document_id, filename, mimetype, document_blob)
        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
