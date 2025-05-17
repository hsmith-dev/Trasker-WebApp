import tkinter as tk
from tkinter import ttk, messagebox

class AddNoteView(tk.Toplevel):
    def __init__(self, parent, controller, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.refresh_callback = refresh_callback
        self.title("Add Note")
        self.geometry("600x400")

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Note text area
        ttk.Label(frame, text="Note:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.note_text = tk.Text(frame, height=10, width=50, wrap="word")
        self.note_text.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Note type dropdown
        ttk.Label(frame, text="Note Type:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.note_type_combo = ttk.Combobox(frame, values=["epic", "sprint", "task", "bug"], state="readonly")
        self.note_type_combo.set("task")  # default value
        self.note_type_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Reference ID entry
        ttk.Label(frame, text="Reference ID:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.reference_entry = ttk.Entry(frame)
        self.reference_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Add Note", command=self.add_note).grid(row=3, column=0, columnspan=2, pady=10)

    def add_note(self):
        note = self.note_text.get("1.0", "end").strip()
        note_type = self.note_type_combo.get().strip()
        reference = self.reference_entry.get().strip()
        reference_id = int(reference) if reference.isdigit() else None

        if not note:
            messagebox.showerror("Error", "Note text cannot be empty!")
            return

        try:
            # Call the Trasker.add_note method, which will now use the current user/team
            self.controller.trasker.add_note(note, note_type, reference_id)
            messagebox.showinfo("Success", "Note added successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add note: {e}")
            return

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
