import tkinter as tk
from tkinter import ttk, messagebox

class EditBugView(tk.Toplevel):
    def __init__(self, parent, controller, bug_id, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.bug_id = bug_id
        self.refresh_callback = refresh_callback

        self.title("Edit Bug")
        self.geometry("600x600")  # increased height to accommodate extra fields

        # Retrieve bug details using a dedicated method (if available) or via list_bug
        bug = self.controller.trasker.get_bug(bug_id)
        if not bug:
            messagebox.showerror("Error", "Bug not found!")
            self.destroy()
            return

        # Unpack bug tuple.
        # Expected new order: (id, title, description, status, created_date, resolved_date, task_id, user_id, team_id)
        _, title, description, status, created_date, resolved_date, task_id, user_id, team_id = bug

        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        row = 0
        # Title field
        ttk.Label(frame, text="Title:", font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ttk.Entry(frame)
        self.title_entry.insert(0, title)
        self.title_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        # Description field
        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(frame, height=8, width=50, wrap="word")
        self.description_text.insert("1.0", description)
        self.description_text.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        # Status dropdown
        ttk.Label(frame, text="Status:", font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        status_options = ["New", "Open", "In Progress", "Resolved", "Closed"]
        self.status_combo = ttk.Combobox(frame, values=status_options, state="readonly")
        self.status_combo.set(status)
        self.status_combo.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        # Created Date entry
        ttk.Label(frame, text="Created Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.created_date_entry = ttk.Entry(frame)
        self.created_date_entry.insert(0, created_date)
        self.created_date_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        # Resolved Date entry
        ttk.Label(frame, text="Resolved Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.resolved_date_entry = ttk.Entry(frame)
        self.resolved_date_entry.insert(0, resolved_date)
        self.resolved_date_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        # Task ID entry – convert the task_id to string explicitly
        ttk.Label(frame, text="Task ID:", font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.task_id_entry = ttk.Entry(frame)
        # Use str() to ensure that the value is a string.
        self.task_id_entry.insert(0, str(task_id))
        self.task_id_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        # Display the User (read-only)
        ttk.Label(frame, text="User:", font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        user_name = user_id if user_id else "N/A"
        self.user_label = ttk.Label(frame, text=user_name)
        self.user_label.grid(row=row, column=1, sticky="w", padx=5, pady=5)

        row += 1
        # Display the Team (read-only)
        ttk.Label(frame, text="Team:", font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        team_name = team_id if team_id else "N/A"
        self.team_label = ttk.Label(frame, text=team_name)
        self.team_label.grid(row=row, column=1, sticky="w", padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        row += 1
        ttk.Button(frame, text="Save Changes", command=self.save_edits).grid(row=row, column=0, columnspan=2, pady=10)

    def save_edits(self):
        new_title = self.title_entry.get().strip()
        new_description = self.description_text.get("1.0", "end").strip()
        new_status = self.status_combo.get().strip()
        new_created_date = self.created_date_entry.get().strip()
        new_resolved_date = self.resolved_date_entry.get().strip()
        new_task_id = self.task_id_entry.get().strip()


        # Call the Trasker.edit_bug method; multi-user context is handled internally.
        self.controller.trasker.edit_bug(
            self.bug_id,
            new_title,
            new_description,
            new_status,
            new_created_date,
            new_resolved_date,
            new_task_id
        )
        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
