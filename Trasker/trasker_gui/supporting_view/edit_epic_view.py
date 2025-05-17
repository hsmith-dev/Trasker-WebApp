import tkinter as tk
from tkinter import ttk, messagebox

class EditEpicView(tk.Toplevel):
    def __init__(self, parent, controller, epic_id, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.epic_id = epic_id
        self.refresh_callback = refresh_callback

        self.title("Edit Epic")
        self.geometry("600x400")

        # Retrieve the epic details.
        # We expect list_epic_by_id to return a tuple such as:
        # (id, name, description, start_date, end_date, user_id, team_id, ...)
        epic = self.controller.trasker.list_epic_by_id(epic_id)
        if not epic:
            messagebox.showerror("Error", "Epic not found!")
            self.destroy()
            return
        # Unpack the first five fields (ignore user_id and team_id).
        _, name, description, start_date, end_date, *_ = epic

        # Build the UI.
        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(frame, text="Name:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.insert(0, name)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(frame, height=6, width=50, wrap="word")
        self.description_text.insert("1.0", description)
        self.description_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Start Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky="w", padx=5, pady=5)
        self.start_date_entry = ttk.Entry(frame)
        self.start_date_entry.insert(0, start_date)
        self.start_date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="End Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(
            row=3, column=0, sticky="w", padx=5, pady=5)
        self.end_date_entry = ttk.Entry(frame)
        self.end_date_entry.insert(0, end_date)
        self.end_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Save Changes", command=self.save_edits).grid(
            row=4, column=0, columnspan=2, pady=10)

    def save_edits(self):
        new_name = self.name_entry.get().strip()
        new_description = self.description_text.get("1.0", "end").strip()
        new_start_date = self.start_date_entry.get().strip()
        new_end_date = self.end_date_entry.get().strip()

        if not new_name or not new_start_date or not new_end_date:
            messagebox.showerror("Error", "Name, Start Date, and End Date are required!")
            return

        # Update the epic using the controller's Trasker method.
        self.controller.trasker.edit_epic(self.epic_id, new_name, new_description, new_start_date, new_end_date)
        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
