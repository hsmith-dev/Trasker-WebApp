# trasker_gui/supporting_view/single_note_view.py
import tkinter as tk
from tkinter import ttk, messagebox

class SingleNoteView(tk.Toplevel):
    def __init__(self, parent, controller, note_id, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.note_id = note_id
        self.refresh_callback = refresh_callback
        self.title("Note Details")
        self.geometry("600x500")

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Retrieve note details
        self.note = self.controller.trasker.get_note(note_id)
        print(self.note_id)
        #notes = self.controller.trasker.list_notes()
        #self.note = next((n for n in notes if n[0] == note_id), None)
        if not self.note:
            messagebox.showerror("Error", "Note not found!")
            self.destroy()
            return

        # Unpack the note tuple.
        # Expected schema: (id, note, note_type, reference_id, user_id, team_id, created_date, updated_date)
        note_id, note_text, note_type, reference_id, user_id, team_id, created_date, updated_date = self.note

        # Retrieve the creator's username and team name.
        username = self.controller.trasker.get_username(user_id) if user_id else "Unknown"
        team_name = self.controller.trasker.get_team_name(team_id) if team_id else "N/A"

        # Display the note details.
        ttk.Label(frame, text="Note:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        text_widget = tk.Text(frame, height=10, width=50, wrap="word")
        text_widget.insert("1.0", note_text)
        text_widget.configure(state="disabled")
        text_widget.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Type:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=note_type).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Reference ID:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=reference_id if reference_id is not None else "None").grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Created by:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=username).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Team:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=team_name).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Created Date:", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=created_date).grid(row=5, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Updated Date:", font=("Arial", 12, "bold")).grid(row=6, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=updated_date).grid(row=6, column=1, sticky="w", padx=5, pady=5)

        ttk.Button(frame, text="Edit Note", command=self.open_edit_view).grid(row=7, column=0, columnspan=2, pady=10)

    def open_edit_view(self):
        from trasker_gui.supporting_view.edit_note_view import EditNoteView
        EditNoteView(self, self.controller, self.note_id, refresh_callback=self.refresh_view)

    def refresh_view(self):
        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
