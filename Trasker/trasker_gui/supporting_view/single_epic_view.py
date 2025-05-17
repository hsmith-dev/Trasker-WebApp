# trasker_gui/supporting_view/single_epic_view.py
import tkinter as tk
from tkinter import ttk, messagebox

class SingleEpicView(tk.Toplevel):
    def __init__(self, parent, controller, epic_id, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.epic_id = epic_id
        self.refresh_callback = refresh_callback

        self.title("Epic Details")
        self.geometry("600x400")

        # Retrieve epic details.
        epic = self.controller.trasker.list_epic_by_id(epic_id)
        if not epic:
            messagebox.showerror("Error", "Epic not found!")
            self.destroy()
            return

        # Expected tuple for multi-user support:
        # (id, name, description, start_date, end_date, user_id, team_id)
        try:
            _, name, description, start_date, end_date, user_id, team_id = epic
        except Exception as e:
            messagebox.showerror("Error", f"Incomplete epic data: {e}")
            self.destroy()
            return

        # Retrieve creator's username and team name via helper methods.
        creator = self.controller.trasker.get_username(user_id) if user_id else "Unknown"
        team_name = self.controller.trasker.get_team_name(team_id) if team_id else "N/A"

        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Epic Name
        ttk.Label(frame, text="Name:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=name).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Epic Description
        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        desc_text = tk.Text(frame, height=6, wrap="word")
        desc_text.insert("1.0", description)
        desc_text.configure(state="disabled")
        desc_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Start Date
        ttk.Label(frame, text="Start Date:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=start_date).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # End Date
        ttk.Label(frame, text="End Date:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=end_date).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Creator information
        ttk.Label(frame, text="Created by:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=creator).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Team information
        ttk.Label(frame, text="Team:", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=team_name).grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # Optional: Add a button to edit the epic.
        edit_button = ttk.Button(self, text="Edit Epic", command=self.open_edit_view)
        edit_button.grid(row=1, column=0, pady=10)

    def open_edit_view(self):
        from trasker_gui.supporting_view.edit_epic_view import EditEpicView
        EditEpicView(self, self.controller, self.epic_id, refresh_callback=self.refresh_view)

    def refresh_view(self):
        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
