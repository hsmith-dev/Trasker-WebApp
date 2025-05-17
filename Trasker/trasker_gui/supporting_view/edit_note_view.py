import tkinter as tk
from tkinter import ttk, messagebox

class EditNoteView(tk.Toplevel):
    def __init__(self, parent, controller, note_id, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.note_id = note_id
        self.refresh_callback = refresh_callback
        self.title("Edit Note")
        self.geometry("600x400")

        # Retrieve the note details using the new get_note method.
        note = self.controller.trasker.get_note(note_id)
        if not note:
            messagebox.showerror("Error", "Note not found!")
            self.destroy()
            return

        # Expected note tuple format:
        # (id, note, note_type, reference_id, user_id, team_id, created_date, updated_date)
        _, note_text, note_type, reference_id, _, _, _, _ = note

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Note text area.
        ttk.Label(frame, text="Note:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="nw", padx=5, pady=5)
        self.note_text = tk.Text(frame, height=10, width=50, wrap="word")
        self.note_text.insert("1.0", note_text)
        self.note_text.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Note type dropdown.
        ttk.Label(frame, text="Note Type:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        self.note_type_combo = ttk.Combobox(frame, values=["epic", "sprint", "task", "bug"], state="readonly")
        self.note_type_combo.set(note_type)
        self.note_type_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Reference ID entry.
        ttk.Label(frame, text="Reference ID:", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky="w", padx=5, pady=5)
        self.reference_entry = ttk.Entry(frame)
        self.reference_entry.insert(0, str(reference_id) if reference_id is not None else "")
        self.reference_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        # Save button.
        ttk.Button(frame, text="Save Changes", command=self.save_changes).grid(
            row=3, column=0, columnspan=2, pady=10)

    def save_changes(self):
        new_note = self.note_text.get("1.0", "end").strip()
        new_note_type = self.note_type_combo.get().strip()
        reference = self.reference_entry.get().strip()
        new_reference_id = int(reference) if reference.isdigit() else None

        if not new_note:
            messagebox.showerror("Error", "Note text cannot be empty!")
            return

        try:
            self.controller.trasker.update_note(self.note_id, new_note, new_note_type, new_reference_id)
            messagebox.showinfo("Success", "Note updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update note: {e}")
            return

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
