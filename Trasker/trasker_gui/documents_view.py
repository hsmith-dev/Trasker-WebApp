import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename
import mimetypes

class DocumentsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Label(self, text="Documents Dashboard", font=("Arial", 24, "bold"))
        header.pack(padx=10, pady=20)

        # --- Filter Panel ---
        filter_panel = ttk.Frame(self)
        filter_panel.pack(fill=tk.X, pady=5)

        ttk.Label(filter_panel, text="Note ID:").pack(side=tk.LEFT, padx=5)
        self.note_id_entry = ttk.Entry(filter_panel, width=10)
        self.note_id_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_panel, text="Filename Contains:").pack(side=tk.LEFT, padx=5)
        self.filename_entry = ttk.Entry(filter_panel, width=20)
        self.filename_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_panel, text="User:").pack(side=tk.LEFT, padx=5)
        self.user_filter = ttk.Combobox(filter_panel, state="readonly")
        self.user_filter.pack(side=tk.LEFT, padx=5)
        self.load_user_dropdown()

        ttk.Label(filter_panel, text="Team:").pack(side=tk.LEFT, padx=5)
        self.team_filter = ttk.Combobox(filter_panel, state="readonly")
        self.team_filter.pack(side=tk.LEFT, padx=5)
        self.load_team_dropdown()

        ttk.Button(filter_panel, text="Apply Filters", command=self.filter_documents).pack(side=tk.LEFT, padx=5)

        # --- Main Panel ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Panel: Document Controls
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        ttk.Button(left_panel, text="+ Add Document", command=self.show_add_document_window, width=20).pack(pady=5)
        ttk.Button(left_panel, text="View Document", command=self.view_document, width=20).pack(pady=5)
        ttk.Button(left_panel, text="Delete Document", command=self.delete_document, width=20).pack(pady=5)

        # Right Panel: Documents Treeview
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        columns = ("ID", "Note ID", "Filename", "Mimetype", "Upload Date", "User", "Team")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind("<Double-1>", self.view_document)

        self.load_documents()

    def load_user_dropdown(self):
        """Populate the user filter combobox based on team membership."""
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
        """Populate the team filter combobox based on teams the current user belongs to."""
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
            # Build a mapping from team name to team id for filtering later.
            self.team_map = {row[1]: row[0] for row in rows}
            self.team_filter["values"] = team_options
            self.team_filter.current(0)
        else:
            self.team_filter["values"] = ["All"]
            self.team_filter.current(0)
            self.team_map = {}

    def load_documents(self):
        """Load documents from the database into the treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        documents = self.controller.trasker.list_all_documents()
        for doc in documents:
            # Ensure the document tuple has 8 columns (pad with None if necessary)
            if len(doc) < 8:
                doc = doc + (None,) * (8 - len(doc))
            user_name = (doc[6]) if doc[6] is not None else "N/A"
            team_name = (doc[7]) if doc[7] is not None else "N/A"
            doc_data = (doc[0], doc[1], doc[2], doc[3], doc[4], user_name, team_name)
            self.tree.insert("", tk.END, values=doc_data)

    def filter_documents(self):
        documents = self.controller.trasker.list_all_documents()
        note_id_filter = self.note_id_entry.get().strip()
        filename_filter = self.filename_entry.get().strip().lower()
        user_filter_value = self.user_filter.get()
        team_filter_value = self.team_filter.get()

        if note_id_filter:
            documents = [doc for doc in documents if doc[1] is not None and str(doc[1]) == note_id_filter]
        if filename_filter:
            documents = [doc for doc in documents if filename_filter in doc[2].lower()]
        if user_filter_value and user_filter_value != "All":
            user_id = self.controller.trasker.get_user_id_from_username(user_filter_value)
            if user_id is not None:
                documents = [doc for doc in documents if len(doc) >= 7 and doc[6] == user_id]
            else:
                documents = []
        if team_filter_value and team_filter_value != "All":
            team_id = self.team_map.get(team_filter_value)
            if team_id is not None:
                documents = [doc for doc in documents if len(doc) >= 8 and doc[7] == team_id]
            else:
                documents = []

        for row in self.tree.get_children():
            self.tree.delete(row)
        for doc in documents:
            if len(doc) < 8:
                doc = doc + (None,) * (8 - len(doc))
            user_name = self.controller.trasker.get_username(doc[6]) if doc[6] is not None else "N/A"
            team_name = self.controller.trasker.get_team_name(doc[7]) if doc[7] is not None else "N/A"
            doc_data = (doc[0], doc[1], doc[2], doc[3], doc[4], user_name, team_name)
            self.tree.insert("", tk.END, values=doc_data)

    def show_add_document_window(self):
        from trasker_gui.supporting_view.add_document_view import AddDocumentView
        AddDocumentView(self, self.controller, refresh_callback=self.load_documents)

    def view_document(self, event=None):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No document selected!")
            return
        doc_values = self.tree.item(selected[0], "values")
        if not doc_values:
            return
        doc_id = doc_values[0]
        from trasker_gui.supporting_view.single_document_view import SingleDocumentView
        SingleDocumentView(self, self.controller, doc_id, refresh_callback=self.load_documents)

    def delete_document(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No document selected!")
            return
        doc_values = self.tree.item(selected[0], "values")
        if not doc_values:
            return
        doc_id = doc_values[0]
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this document%s"):
            self.controller.trasker.delete_document(doc_id)
            self.load_documents()
