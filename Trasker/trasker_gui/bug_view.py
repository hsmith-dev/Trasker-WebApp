import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class BugView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Label(self, text="Bugs Dashboard", font=("Arial", 24, "bold"))
        header.pack(padx=10, pady=20)

        # --- Filter Panel ---
        filter_panel = ttk.Frame(self)
        filter_panel.pack(fill=tk.X, pady=5)

        # Row 1: Related Task ID filter
        ttk.Label(filter_panel, text="Related Task ID:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.task_id_entry = ttk.Entry(filter_panel, width=10)
        self.task_id_entry.grid(row=0, column=1, padx=5, pady=2)

        # Row 2: Created Date Range filters
        ttk.Label(filter_panel, text="Created Date From (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.created_from_entry = ttk.Entry(filter_panel, width=12)
        self.created_from_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(filter_panel, text="To:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.created_to_entry = ttk.Entry(filter_panel, width=12)
        self.created_to_entry.grid(row=1, column=3, padx=5, pady=2)

        # Row 3: Resolved Date Range filters
        ttk.Label(filter_panel, text="Resolved Date From (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.resolved_from_entry = ttk.Entry(filter_panel, width=12)
        self.resolved_from_entry.grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(filter_panel, text="To:").grid(row=2, column=2, padx=5, pady=2, sticky="w")
        self.resolved_to_entry = ttk.Entry(filter_panel, width=12)
        self.resolved_to_entry.grid(row=2, column=3, padx=5, pady=2)

        # Row 4: New filters for User and Team.
        ttk.Label(filter_panel, text="User:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.user_filter = ttk.Combobox(filter_panel, state="readonly")
        self.user_filter.grid(row=3, column=1, padx=5, pady=2)
        self.load_user_dropdown()

        ttk.Label(filter_panel, text="Team:").grid(row=3, column=2, padx=5, pady=2, sticky="w")
        self.team_filter = ttk.Combobox(filter_panel, state="readonly")
        self.team_filter.grid(row=3, column=3, padx=5, pady=2)
        self.load_team_dropdown()

        # Button to apply all filters.
        ttk.Button(filter_panel, text="Apply Filters", command=self.filter_bugs).grid(row=4, column=0, columnspan=4, pady=5)

        # --- Main Panel ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Panel: Bug Controls
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        ttk.Button(left_panel, text="+ Add Bug", command=self.show_add_bug_window, width=20).pack(pady=5)
        ttk.Button(left_panel, text="View Bug", command=self.view_bug_details, width=20).pack(pady=5)
        ttk.Button(left_panel, text="Edit Bug", command=self.edit_bug, width=20).pack(pady=5)
        ttk.Button(left_panel, text="Delete Bug", command=self.delete_bug, width=20).pack(pady=5)

        # Right Panel: Bug List (Treeview)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # Updated columns include User and Team.
        columns = ("ID", "Title", "Description", "Status", "Created Date", "Resolved Date", "Task ID", "User", "Team")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind("<Double-1>", self.view_bug_details)

        # Initially load all bugs.
        self.load_bugs()

    def load_user_dropdown(self):
        """Populate the user filter combobox with users accessible to the current user (e.g. team members)."""
        if hasattr(self.controller.trasker, "current_team") and self.controller.trasker.current_team:
            current_team = self.controller.trasker.current_team
            if isinstance(current_team, int):
                current_team_id = current_team
            else:
                current_team_id = current_team[0]
            query = """
                SELECT u.id, u.username
                FROM users u
                JOIN user_team ut ON u.id = ut.user_id
                WHERE ut.team_id = %s
            """
            rows = self.controller.trasker.db_execute(query, (current_team_id,), fetch=True)
            user_options = ["All"] + [row[1] for row in rows]
            self.user_filter["values"] = user_options
            self.user_filter.current(0)
        else:
            self.user_filter["values"] = ["All"]
            self.user_filter.current(0)

    def load_team_dropdown(self):
        """Populate the team filter combobox with teams the current user belongs to."""
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
            team_options = ["All"] + [row[1] for row in rows]
            # Build a mapping from team name to team id.
            self.team_map = {row[1]: row[0] for row in rows}
            self.team_filter["values"] = team_options
            self.team_filter.current(0)
        else:
            self.team_filter["values"] = ["All"]
            self.team_filter.current(0)
            self.team_map = {}

    def load_bugs(self):
        """Load bugs from the database into the treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        bugs = self.controller.trasker.list_all_bugs()  # Ensure this is implemented in Trasker.
        for bug in bugs:
            # Bug tuple is assumed to be:
            # (id, title, description, status, created_date, resolved_date, task_id, user_id, team_id)
            user_name = (bug[7]) if bug[7] is not None else "N/A"
            team_name = (bug[8]) if bug[8] is not None else "N/A"
            values = (bug[0], bug[1], bug[2], bug[3], bug[4], bug[5], bug[6], user_name, team_name)
            self.tree.insert("", tk.END, values=values)

    def filter_bugs(self):
        """Filter bugs based on related task ID, created/resolved date ranges, user, and team."""
        bugs = self.controller.trasker.list_all_bugs()

        # Filter by related task ID.
        task_id_filter = self.task_id_entry.get().strip()
        if task_id_filter:
            bugs = [bug for bug in bugs if bug[6] is not None and str(bug[6]) == task_id_filter]

        # Filter by Created Date Range.
        created_from_str = self.created_from_entry.get().strip()
        created_to_str = self.created_to_entry.get().strip()
        if created_from_str or created_to_str:
            filtered = []
            try:
                created_from = datetime.strptime(created_from_str, "%Y-%m-%d") if created_from_str else None
                created_to = datetime.strptime(created_to_str, "%Y-%m-%d") if created_to_str else None
            except ValueError:
                messagebox.showerror("Error", "Created Date filters must be in YYYY-MM-DD format")
                return
            for bug in bugs:
                created_date_str = bug[4]
                try:
                    created_date = datetime.strptime(created_date_str, "%Y-%m-%d")
                except (ValueError, TypeError):
                    continue
                if created_from and created_to:
                    if created_from <= created_date <= created_to:
                        filtered.append(bug)
                elif created_from:
                    if created_date >= created_from:
                        filtered.append(bug)
                elif created_to:
                    if created_date <= created_to:
                        filtered.append(bug)
            bugs = filtered

        # Filter by Resolved Date Range.
        resolved_from_str = self.resolved_from_entry.get().strip()
        resolved_to_str = self.resolved_to_entry.get().strip()
        if resolved_from_str or resolved_to_str:
            filtered = []
            try:
                resolved_from = datetime.strptime(resolved_from_str, "%Y-%m-%d") if resolved_from_str else None
                resolved_to = datetime.strptime(resolved_to_str, "%Y-%m-%d") if resolved_to_str else None
            except ValueError:
                messagebox.showerror("Error", "Resolved Date filters must be in YYYY-MM-DD format")
                return
            for bug in bugs:
                resolved_date_str = bug[5]
                if not resolved_date_str:
                    continue
                try:
                    resolved_date = datetime.strptime(resolved_date_str, "%Y-%m-%d")
                except ValueError:
                    continue
                if resolved_from and resolved_to:
                    if resolved_from <= resolved_date <= resolved_to:
                        filtered.append(bug)
                elif resolved_from:
                    if resolved_date >= resolved_from:
                        filtered.append(bug)
                elif resolved_to:
                    if resolved_date <= resolved_to:
                        filtered.append(bug)
            bugs = filtered

        # Filter by User.
        user_filter_value = self.user_filter.get()
        if user_filter_value and user_filter_value != "All":
            user_id = self.controller.trasker.get_user_id_from_username(user_filter_value)
            if user_id is not None:
                bugs = [bug for bug in bugs if bug[7] == user_id]
            else:
                bugs = []

        # Filter by Team.
        team_filter_value = self.team_filter.get()
        if team_filter_value and team_filter_value != "All":
            team_id = self.team_map.get(team_filter_value)
            if team_id is not None:
                bugs = [bug for bug in bugs if bug[8] == team_id]
            else:
                bugs = []

        # Update the treeview.
        for row in self.tree.get_children():
            self.tree.delete(row)
        for bug in bugs:
            user_name = self.controller.trasker.get_username(bug[7]) if bug[7] is not None else "N/A"
            team_name = self.controller.trasker.get_team_name(bug[8]) if bug[8] is not None else "N/A"
            values = (bug[0], bug[1], bug[2], bug[3], bug[4], bug[5], bug[6], user_name, team_name)
            self.tree.insert("", tk.END, values=values)

    def show_add_bug_window(self):
        from trasker_gui.supporting_view.add_bug_view import AddBugView
        AddBugView(self, self.controller, refresh_callback=self.load_bugs)

    def view_bug_details(self, event=None):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No bug selected!")
            return
        bug_values = self.tree.item(selected[0], "values")
        if not bug_values:
            return
        bug_id = bug_values[0]
        from trasker_gui.supporting_view.single_bug_view import SingleBugView
        SingleBugView(self, self.controller, bug_id, refresh_callback=self.load_bugs)

    def edit_bug(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No bug selected!")
            return
        bug_values = self.tree.item(selected[0], "values")
        if not bug_values:
            return
        bug_id = bug_values[0]
        from trasker_gui.supporting_view.edit_bug_view import EditBugView
        EditBugView(self, self.controller, bug_id, refresh_callback=self.load_bugs)

    def delete_bug(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No bug selected!")
            return
        bug_values = self.tree.item(selected[0], "values")
        if not bug_values:
            return
        bug_id = bug_values[0]
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this bug%s"):
            self.controller.trasker.delete_bug(bug_id)
            self.load_bugs()
