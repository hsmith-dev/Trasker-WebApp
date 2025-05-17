# trasker_gui/single_sprint_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from trasker_gui.supporting_view.edit_sprint_view import EditSprintView

class SingleSprintView(tk.Toplevel):
    def __init__(self, parent, controller, sprint_id, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.sprint_id = sprint_id
        self.refresh_callback = refresh_callback

        self.title("Sprint Details")
        self.geometry("600x500")

        # Retrieve the sprint details.
        sprint = self.controller.trasker.list_sprint_by_id(self.sprint_id)
        if not sprint:
            messagebox.showerror("Error", "Sprint not found!")
            self.destroy()
            return

        # Updated sprint tuple expected:
        # (id, title, description, start_date, end_date, epic_id, user_id, team_id)
        _, title, description, start_date, end_date, epic_id, user_id, team_id = sprint

        # Create a frame for displaying details.
        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Display Sprint Title.
        ttk.Label(frame, text="Title:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=title).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Display Description.
        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        desc_text = tk.Text(frame, height=8, wrap="word")
        desc_text.insert("1.0", description)
        desc_text.configure(state="disabled")
        desc_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Display Start Date.
        ttk.Label(frame, text="Start Date:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=start_date).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Display End Date.
        ttk.Label(frame, text="End Date:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=end_date).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Display the creator (user) name.
        created_by = self.controller.trasker.get_username(user_id) if user_id else "Unknown"
        ttk.Label(frame, text="Created by:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=created_by).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Display the team name.
        team_name = self.controller.trasker.get_team_name(team_id) if team_id else "N/A"
        ttk.Label(frame, text="Team:", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=team_name).grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # Button to edit the sprint.
        ttk.Button(self, text="Edit Sprint", command=self.open_edit_view).grid(row=6, column=0, columnspan=2, pady=10)

    def open_edit_view(self):
        from trasker_gui.supporting_view.edit_sprint_view import EditSprintView
        EditSprintView(self, self.controller, self.sprint_id, refresh_callback=self.refresh_view)

    def refresh_view(self):
        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
