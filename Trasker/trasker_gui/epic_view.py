import tkinter as tk
from tkinter import ttk, messagebox


class EpicView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Reference to your main controller (TraskerGUI)

        # Header label for the view
        header = ttk.Label(self, text="Epics Dashboard", font=("Arial", 24, "bold"))
        header.pack(padx=10, pady=20)

        # Main container frame (left panel for controls, right panel for the list)
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # LEFT PANEL: Epic controls and filters
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # --- Team filter ---
        ttk.Label(left_panel, text="Filter by Team:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        self.team_filter = ttk.Combobox(left_panel, state="readonly")
        self.team_filter.pack(pady=5, fill=tk.X, padx=5)
        self.team_filter.bind("<<ComboboxSelected>>", lambda e: self.load_epics())
        self.load_team_dropdown()

        # Epic management buttons
        ttk.Button(left_panel, text="+ Add Epic", command=self.show_add_epic_window, width=20).pack(pady=5)
        ttk.Button(left_panel, text="View Epic", command=self.view_epic_details, width=20).pack(pady=5)
        ttk.Button(left_panel, text="Edit Epic", command=self.edit_epic, width=20).pack(pady=5)
        ttk.Button(left_panel, text="Delete Epic", command=self.delete_epic, width=20).pack(pady=5)

        # RIGHT PANEL: Epic list (Treeview)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Define the columns for epics (adjust as needed to match your db schema)
        self.tree = ttk.Treeview(right_panel,
                                 columns=("ID", "Name", "Description", "Start Date", "End Date", "Owner", "Team"),
                                 show="headings")
        for col in ("ID", "Name", "Description", "Start Date", "End Date", "Owner", "Team"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # (Optional) Bind a double-click event to view details.
        self.tree.bind("<Double-1>", self.view_epic_details)

        # Load the epics when the view is created.
        self.load_epics()

    def load_team_dropdown(self):
        """Load the teams the current user belongs to into the team filter combobox."""
        # Query the teams for the current user.
        # (We use the controller's trasker.db_execute method directly.)
        user_id = self.controller.trasker.current_user[0]
        query = """
            SELECT t.name 
            FROM teams t
            JOIN user_team ut ON t.id = ut.team_id
            WHERE ut.user_id = %s
        """
        teams = self.controller.trasker.db_execute(query, (user_id,), fetch=True)
        team_names = ["All Teams"] + [team[0] for team in teams]
        self.team_filter['values'] = team_names
        self.team_filter.current(0)

    def load_epics(self):
        """Load epics from the database into the Treeview, optionally filtering by team."""
        # Clear any existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Get all epics visible to the user (the Trasker.list_epics method already filters by current user/team)
        all_epics = self.controller.trasker.list_epics()
        # Determine the team filter value.
        team_filter_value = self.team_filter.get()
        if team_filter_value and team_filter_value != "All Teams":
            # Filter epics where the team name matches the selection.
            filtered_epics = [epic for epic in all_epics if epic[6] == team_filter_value]
        else:
            filtered_epics = all_epics
        # Insert each epic into the Treeview.
        for epic in filtered_epics:
            # Expected epic tuple: (id, name, description, start_date, end_date, owner_username, team_name)
            self.tree.insert("", tk.END, values=epic)

    def show_add_epic_window(self):
        """Open the add epic view."""
        from trasker_gui.supporting_view.add_epic_view import AddEpicView
        AddEpicView(self, self.controller, refresh_callback=self.load_epics)

    def view_epic_details(self, event=None):
        """Open the single epic view for the selected epic."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No epic selected!")
            return
        epic_values = self.tree.item(selected[0], "values")
        if not epic_values:
            return
        epic_id = epic_values[0]
        from trasker_gui.supporting_view.single_epic_view import SingleEpicView
        SingleEpicView(self, self.controller, epic_id, refresh_callback=self.load_epics)

    def edit_epic(self):
        """Open the edit epic view for the selected epic."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No epic selected!")
            return
        epic_values = self.tree.item(selected[0], "values")
        if not epic_values:
            return
        epic_id = epic_values[0]
        from trasker_gui.supporting_view.edit_epic_view import EditEpicView
        EditEpicView(self, self.controller, epic_id, refresh_callback=self.load_epics)

    def delete_epic(self):
        """Delete the selected epic after confirmation."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No epic selected!")
            return
        epic_values = self.tree.item(selected[0], "values")
        if not epic_values:
            return
        epic_id = epic_values[0]
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this epic%s"):
            self.controller.trasker.delete_epic(epic_id)
            self.load_epics()
