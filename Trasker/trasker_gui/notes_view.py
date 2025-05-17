import tkinter as tk
from tkinter import ttk, messagebox

class NotesView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Label(self, text="Notes Dashboard", font=("Arial", 24, "bold"))
        header.pack(padx=10, pady=20)

        # --- Filter Panel ---
        filter_panel = ttk.Frame(self)
        filter_panel.pack(fill=tk.X, pady=5)

        # Note Type filter combobox
        ttk.Label(filter_panel, text="Note Type:").pack(side=tk.LEFT, padx=5)
        self.note_type_filter = ttk.Combobox(filter_panel, state="readonly")
        self.note_type_filter.pack(side=tk.LEFT, padx=5)
        # "All" means no filtering by type.
        self.note_type_filter["values"] = ["All", "epic", "sprint", "task", "bug"]
        self.note_type_filter.current(0)
        self.note_type_filter.bind("<<ComboboxSelected>>", self.filter_notes)

        # Reference ID filter entry
        ttk.Label(filter_panel, text="Reference ID:").pack(side=tk.LEFT, padx=5)
        self.ref_id_entry = ttk.Entry(filter_panel, width=10)
        self.ref_id_entry.pack(side=tk.LEFT, padx=5)

        # User filter combobox
        ttk.Label(filter_panel, text="User:").pack(side=tk.LEFT, padx=5)
        self.user_filter = ttk.Combobox(filter_panel, state="readonly")
        self.user_filter.pack(side=tk.LEFT, padx=5)
        self.load_user_dropdown()

        # Team filter combobox
        ttk.Label(filter_panel, text="Team:").pack(side=tk.LEFT, padx=5)
        self.team_filter = ttk.Combobox(filter_panel, state="readonly")
        self.team_filter.pack(side=tk.LEFT, padx=5)
        self.load_team_dropdown()

        ttk.Button(filter_panel, text="Apply Filters", command=self.filter_notes).pack(side=tk.LEFT, padx=5)

        # --- Main Panel ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Panel: Note Controls
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        ttk.Button(left_panel, text="+ Add Note", command=self.show_add_note_window, width=20).pack(pady=5)
        ttk.Button(left_panel, text="View Note", command=self.view_note_details, width=20).pack(pady=5)
        ttk.Button(left_panel, text="Edit Note", command=self.edit_note, width=20).pack(pady=5)
        ttk.Button(left_panel, text="Delete Note", command=self.delete_note, width=20).pack(pady=5)

        # Right Panel: Notes Treeview
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # Extend columns to include User and Team.
        columns = ("ID", "Note", "Note Type", "Reference ID", "User", "Team", "Created Date", "Updated Date")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind("<Double-1>", self.view_note_details)

        self.load_notes()

    def load_user_dropdown(self):
        """Populate the user filter combobox with users available to the current user (e.g. team members)."""
        # Assume the current team is stored in self.controller.trasker.current_team.
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

    def load_notes(self):
        """Load all notes into the treeview, applying current filters if any."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Get filter values.
        note_type = self.note_type_filter.get()
        if note_type == "All":
            note_type = None
        ref_id = self.ref_id_entry.get().strip() or None

        user_filter_value = self.user_filter.get()
        if user_filter_value == "All":
            user_filter_value = None

        team_filter_value = self.team_filter.get()
        if team_filter_value == "All":
            team_filter_value = None

        # Get notes from the Trasker instance.
        notes = self.controller.trasker.list_notes(note_type, ref_id)

        # Further filter by user.
        if user_filter_value:
            # Assuming that in the notes tuple, user_id is at index 4.
            # (You might need to adjust this based on your actual query result.)
            user_id = self.controller.trasker.get_user_id_from_username(user_filter_value)
            if user_id is not None:
                notes = [note for note in notes if note[4] == user_id]
            else:
                notes = []

        # Further filter by team.
        if team_filter_value:
            # Convert the team name to team id using self.team_map.
            team_id = self.team_map.get(team_filter_value)
            if team_id is not None:
                # Assuming that in the notes tuple, team_id is at index 5.
                notes = [note for note in notes if note[5] == team_id]
            else:
                notes = []

        # Insert notes into the treeview. For display, we convert user_id and team_id to names.
        for note in notes:
            # Note tuple is assumed to be:
            # (id, note, note_type, reference_id, user_id, team_id, created_date, updated_date)
            user_name = self.controller.trasker.get_username(note[4]) if note[4] else "N/A"
            team_name = self.controller.trasker.get_team_name(note[5]) if note[5] else "N/A"
            values = (note[0], note[1], note[2], note[3], user_name, team_name, note[6], note[7])
            self.tree.insert("", tk.END, values=values)

    def filter_notes(self, event=None):
        self.load_notes()

    def show_add_note_window(self):
        from trasker_gui.supporting_view.add_note_view import AddNoteView
        AddNoteView(self, self.controller, refresh_callback=self.load_notes)

    def view_note_details(self, event=None):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No note selected!")
            return
        note_values = self.tree.item(selected[0], "values")
        if not note_values:
            return
        note_id = note_values[0]
        from trasker_gui.supporting_view.single_note_view import SingleNoteView
        SingleNoteView(self, self.controller, note_id, refresh_callback=self.load_notes)

    def edit_note(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No note selected!")
            return
        note_values = self.tree.item(selected[0], "values")
        if not note_values:
            return
        note_id = note_values[0]
        from trasker_gui.supporting_view.edit_note_view import EditNoteView
        EditNoteView(self, self.controller, note_id, refresh_callback=self.load_notes)

    def delete_note(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No note selected!")
            return
        note_values = self.tree.item(selected[0], "values")
        if not note_values:
            return
        note_id = note_values[0]
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this note%s"):
            self.controller.trasker.delete_note(note_id)
            self.load_notes()
