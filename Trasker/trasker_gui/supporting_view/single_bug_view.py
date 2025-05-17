import tkinter as tk
from tkinter import ttk, messagebox

class SingleBugView(tk.Toplevel):
    def __init__(self, parent, controller, bug_id, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.bug_id = bug_id
        self.refresh_callback = refresh_callback

        self.title("Bug Details")
        self.geometry("600x600")

        # Retrieve the bug using the new get_bug() method.
        bug = self.controller.trasker.get_bug(bug_id)
        if not bug:
            messagebox.showerror("Error", "Bug not found!")
            self.destroy()
            return

        # Expected bug tuple from PostgreSQL:
        # (id, title, description, status, created_date, resolved_date, task_id, username, team_name)
        bug_id, title, description, status, created_date, resolved_date, task_id, username, team_name = bug

        # Create the main frame.
        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        row_idx = 0

        ttk.Label(frame, text="Title:", font=("Arial", 12, "bold")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=title).grid(row=row_idx, column=1, sticky="w", padx=5, pady=5)
        row_idx += 1

        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(row=row_idx, column=0, sticky="nw", padx=5, pady=5)
        desc_text = tk.Text(frame, height=8, wrap="word")
        desc_text.insert("1.0", description)
        desc_text.configure(state="disabled")
        desc_text.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(frame, text="Status:", font=("Arial", 12, "bold")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=status).grid(row=row_idx, column=1, sticky="w", padx=5, pady=5)
        row_idx += 1

        ttk.Label(frame, text="Created Date:", font=("Arial", 12, "bold")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=created_date).grid(row=row_idx, column=1, sticky="w", padx=5, pady=5)
        row_idx += 1

        ttk.Label(frame, text="Resolved Date:", font=("Arial", 12, "bold")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=resolved_date if resolved_date else "N/A").grid(row=row_idx, column=1, sticky="w", padx=5, pady=5)
        row_idx += 1

        ttk.Label(frame, text="Related Task ID:", font=("Arial", 12, "bold")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=task_id if task_id else "N/A").grid(row=row_idx, column=1, sticky="w", padx=5, pady=5)
        row_idx += 1

        ttk.Label(frame, text="Assigned User:", font=("Arial", 12, "bold")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=username).grid(row=row_idx, column=1, sticky="w", padx=5, pady=5)
        row_idx += 1

        ttk.Label(frame, text="Team:", font=("Arial", 12, "bold")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=team_name).grid(row=row_idx, column=1, sticky="w", padx=5, pady=5)
        row_idx += 1

        # Button to open the edit view.
        ttk.Button(self, text="Edit Bug", command=self.open_edit_view).grid(row=row_idx, column=0, columnspan=2, pady=10)

    def open_edit_view(self):
        from trasker_gui.supporting_view.edit_bug_view import EditBugView
        EditBugView(self, self.controller, self.bug_id, refresh_callback=self.refresh_view)

    def refresh_view(self):
        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
