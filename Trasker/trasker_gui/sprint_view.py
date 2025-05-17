import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class SprintView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Label(self, text="Sprint Dashboard", font=("Arial", 24, "bold"))
        header.pack(padx=10, pady=20)

        # --- Filter Panel ---
        filter_panel = ttk.Frame(self)
        filter_panel.pack(fill=tk.X, pady=5)

        # Epic filter combobox
        ttk.Label(filter_panel, text="Filter by Epic:").pack(side=tk.LEFT, padx=5)
        self.epic_filter = ttk.Combobox(filter_panel, state="readonly")
        self.epic_filter.pack(side=tk.LEFT, padx=5)
        self.epic_filter.bind("<<ComboboxSelected>>", self.refresh_sprints)

        # Team filter combobox
        ttk.Label(filter_panel, text="Filter by Team:").pack(side=tk.LEFT, padx=5)
        self.team_filter = ttk.Combobox(filter_panel, state="readonly")
        self.team_filter.pack(side=tk.LEFT, padx=5)
        self.team_filter.bind("<<ComboboxSelected>>", self.refresh_sprints)

        # Date range filters
        ttk.Label(filter_panel, text="From (YYYY-MM-DD):").pack(side=tk.LEFT, padx=5)
        self.from_date_entry = ttk.Entry(filter_panel, width=12)
        self.from_date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_panel, text="To (YYYY-MM-DD):").pack(side=tk.LEFT, padx=5)
        self.to_date_entry = ttk.Entry(filter_panel, width=12)
        self.to_date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_panel, text="Apply Date Filter", command=self.refresh_sprints).pack(side=tk.LEFT, padx=5)

        # Load dropdown data
        self.load_epic_dropdown()
        self.load_team_dropdown()

        # --- Main Panel for Sprint List ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Panel: Sprint Controls
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        ttk.Button(left_panel, text="+ Add Sprint", command=self.show_add_sprint_window, width=20).pack(pady=5)
        ttk.Button(left_panel, text="View Sprint", command=self.view_sprint_details, width=20).pack(pady=5)
        ttk.Button(left_panel, text="Edit Sprint", command=self.edit_sprint, width=20).pack(pady=5)
        ttk.Button(left_panel, text="Delete Sprint", command=self.delete_sprint, width=20).pack(pady=5)

        # Right Panel: Sprint List (Treeview)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(right_panel,
                                 columns=("ID", "Title", "Description", "Start Date", "End Date", "Epic ID", "Team"),
                                 show="headings")
        for col in ("ID", "Title", "Description", "Start Date", "End Date", "Epic ID", "Team"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind("<Double-1>", self.view_sprint_details)

        # Load sprints initially
        self.refresh_sprints()

    def load_epic_dropdown(self):
        """Populate the epic filter combobox."""
        epics = self.controller.trasker.list_epics()
        epic_names = ["All Epics"] + [epic[1] for epic in epics]
        self.epic_filter["values"] = epic_names
        self.epic_filter.current(0)

    def load_team_dropdown(self):
        """Populate the team filter combobox with teams for the current user."""
        if hasattr(self.controller.trasker, "current_user") and self.controller.trasker.current_user:
            current_user = self.controller.trasker.current_user
            if isinstance(current_user, tuple):
                current_user_id = current_user[0]
            else:
                current_user_id = current_user
            query = """
                SELECT t.id, t.name
                FROM teams t
                JOIN user_team ut ON t.id = ut.team_id
                WHERE ut.user_id = %s
            """
            rows = self.controller.trasker.db_execute(query, (current_user_id,), fetch=True)
            team_names = ["All Teams"]
            self.team_map = {}
            for row in rows:
                team_id, team_name = row
                team_names.append(team_name)
                self.team_map[team_name] = team_id
            self.team_filter["values"] = team_names
            self.team_filter.current(0)
        else:
            self.team_filter["values"] = ["All Teams"]
            self.team_filter.current(0)

    def refresh_sprints(self, event=None):
        """Reload sprints based on epic, team, and date range filters."""
        sprints = self.controller.trasker.list_sprints()  # Expecting sprint tuple: (id, title, description, start_date, end_date, epic_id, user_id, team_id)

        # Epic filtering.
        epic_filter = self.epic_filter.get()
        if epic_filter != "All Epics":
            epics = self.controller.trasker.list_epics()
            epic_id = next((epic[0] for epic in epics if epic[1] == epic_filter), None)
            if epic_id:
                sprints = [s for s in sprints if s[5] == epic_id]
            else:
                sprints = []

        # Team filtering.
        team_filter = self.team_filter.get()
        if team_filter != "All Teams":
            team_id = self.team_map.get(team_filter)
            if team_id:
                sprints = [s for s in sprints if s[7] == team_filter]
            else:
                sprints = []

        # Date range filtering.
        from_date_str = self.from_date_entry.get().strip()
        to_date_str = self.to_date_entry.get().strip()
        if from_date_str or to_date_str:
            filtered = []
            try:
                from_dt = datetime.strptime(from_date_str, "%Y-%m-%d") if from_date_str else None
                to_dt = datetime.strptime(to_date_str, "%Y-%m-%d") if to_date_str else None
            except ValueError:
                messagebox.showerror("Error", "Date format must be YYYY-MM-DD")
                return
            for sprint in sprints:
                sprint_start = sprint[3]
                sprint_end = sprint[4]
                try:
                    sprint_start_dt = datetime.strptime(sprint_start, "%Y-%m-%d")
                    sprint_end_dt = datetime.strptime(sprint_end, "%Y-%m-%d")
                except ValueError:
                    continue
                if from_dt and to_dt:
                    if (from_dt <= sprint_start_dt <= to_dt) or (from_dt <= sprint_end_dt <= to_dt):
                        filtered.append(sprint)
                elif from_dt and (sprint_start_dt >= from_dt or sprint_end_dt >= from_dt):
                    filtered.append(sprint)
                elif to_dt and (sprint_start_dt <= to_dt or sprint_end_dt <= to_dt):
                    filtered.append(sprint)
            sprints = filtered

        self.load_sprints_into_tree(sprints)

    def load_sprints_into_tree(self, sprints):
        """Clear the treeview and insert the provided sprint data."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for sprint in sprints:
            # Here we display: ID, Title, Description, Start Date, End Date, Epic ID, and Team name.
            team_name = "N/A"
            if len(sprint) >= 8:
                team_name = sprint[7]
            self.tree.insert("", tk.END, values=(sprint[0], sprint[1], sprint[2], sprint[3], sprint[4], sprint[5], team_name))

    def show_add_sprint_window(self):
        from trasker_gui.supporting_view.add_sprint_view import AddSprintView
        AddSprintView(self, self.controller, refresh_callback=self.refresh_sprints)

    def view_sprint_details(self, event=None):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No sprint selected!")
            return
        sprint_values = self.tree.item(selected[0], "values")
        if not sprint_values:
            return
        sprint_id = sprint_values[0]
        from trasker_gui.supporting_view.single_sprint_view import SingleSprintView
        SingleSprintView(self, self.controller, sprint_id, refresh_callback=self.refresh_sprints)

    def edit_sprint(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No sprint selected!")
            return
        sprint_values = self.tree.item(selected[0], "values")
        if not sprint_values:
            return
        sprint_id = sprint_values[0]
        from trasker_gui.supporting_view.edit_sprint_view import EditSprintView
        EditSprintView(self, self.controller, sprint_id, refresh_callback=self.refresh_sprints)

    def delete_sprint(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No sprint selected!")
            return
        sprint_values = self.tree.item(selected[0], "values")
        if not sprint_values:
            return
        sprint_id = sprint_values[0]
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this sprint%s"):
            self.controller.trasker.delete_sprint(sprint_id)
            self.refresh_sprints()
