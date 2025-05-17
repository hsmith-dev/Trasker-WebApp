import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AddBugView(tk.Toplevel):
    def __init__(self, parent, controller, refresh_callback):
        super().__init__(parent)
        self.controller = controller
        self.refresh_callback = refresh_callback

        self.title("Add Bug")
        self.geometry("600x500")

        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        ttk.Label(frame, text="Title:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ttk.Entry(frame)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Description
        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(frame, height=8, width=50, wrap="word")
        self.description_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Status dropdown
        ttk.Label(frame, text="Status:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        status_options = ["New", "Open", "In Progress", "Resolved", "Closed"]
        self.status_combo = ttk.Combobox(frame, values=status_options, state="readonly")
        self.status_combo.set("New")
        self.status_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Created Date
        ttk.Label(frame, text="Created Date:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.created_date_entry = ttk.Entry(frame)
        self.created_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.created_date_entry.insert(0, current_time)

        # Resolved Date (optional)
        ttk.Label(frame, text="Resolved Date:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.resolved_date_entry = ttk.Entry(frame)
        self.resolved_date_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        # Task ID (optional)
        ttk.Label(frame, text="Task ID:", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.task_id_entry = ttk.Entry(frame)
        self.task_id_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Add Bug", command=self.submit_bug).grid(row=6, column=0, columnspan=2, pady=10)

    def submit_bug(self):
        title = self.title_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        status = self.status_combo.get().strip()
        created_date = self.created_date_entry.get().strip()
        resolved_date = self.resolved_date_entry.get().strip()
        task_id = self.task_id_entry.get().strip()

        if not title or not created_date:
            messagebox.showerror("Error", "Title and Created Date are required!")
            return

        # Retrieve current user and team from the controller's Trasker instance.
        # (Adjust these lines if your implementation differs.)
        current_user = self.controller.trasker.current_user
        if isinstance(current_user, tuple):
            user_id = current_user[0]
        else:
            user_id = current_user

        current_team = self.controller.trasker.current_team
        if isinstance(current_team, tuple):
            team_id = current_team[0]
        else:
            team_id = current_team

        # Convert task_id to integer if provided.
        if task_id:
            try:
                task_id = int(task_id)
            except ValueError:
                messagebox.showerror("Error", "Task ID must be an integer!")
                return
        else:
            task_id = None

        try:
            # Call the Trasker method to add a bug with user and team association.
            self.controller.trasker.add_bug(title, description, status, created_date, resolved_date, task_id, user_id, team_id)
            messagebox.showinfo("Success", "Bug added successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add bug: {e}")
            return

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
