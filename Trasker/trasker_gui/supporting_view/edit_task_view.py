import tkinter as tk
from tkinter import ttk, messagebox

class EditTaskView(tk.Toplevel):
    def __init__(self, parent, controller, task_id, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.task_id = task_id
        self.refresh_callback = refresh_callback
        self.title("Edit Task")
        self.geometry("1800x900")

        # Retrieve task details. We assume list_all_tasks returns tasks in the order:
        # (id, title, description, due_date, status, category, priority, recurrence, parent_task_id, sprint_id, user_id, team_id)
        tasks = self.controller.trasker.list_all_tasks()
        task = next((t for t in tasks if t[0] == task_id), None)
        if not task:
            messagebox.showerror("Error", "Task not found!")
            self.destroy()
            return

        # Unpack the basic task fields.
        # For our purposes, we only need the first 7 fields plus the assigned user and team.
        # (Indexes: 0=id, 1=title, 2=description, 3=due_date, 4=status, 5=category, 6=priority,
        # 10=user_id, 11=team_id)
        _, title, description, due_date, status, category, priority = task[:7]
        current_user_id = task[10] if len(task) > 10 else None
        current_team_id = task[11] if len(task) > 11 else None

        # Create the main frame.
        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        ttk.Label(frame, text="Title:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ttk.Entry(frame)
        self.title_entry.insert(0, title)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Description (multi-line)
        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(frame, height=10, width=50, wrap="word")
        self.description_text.insert("1.0", description)
        self.description_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Due Date
        ttk.Label(frame, text="Due Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky="w", padx=5, pady=5)
        self.due_date_entry = ttk.Entry(frame)
        self.due_date_entry.insert(0, due_date)
        self.due_date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Status dropdown
        ttk.Label(frame, text="Status:", font=("Arial", 12, "bold")).grid(
            row=3, column=0, sticky="w", padx=5, pady=5)
        status_options = ["Holding", "Pending", "In Progress", "Completed", "Archived"]
        self.status_combo = ttk.Combobox(frame, values=status_options, state="readonly")
        self.status_combo.set(status)
        self.status_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Category
        ttk.Label(frame, text="Category:", font=("Arial", 12, "bold")).grid(
            row=4, column=0, sticky="w", padx=5, pady=5)
        self.category_entry = ttk.Entry(frame)
        self.category_entry.insert(0, category)
        self.category_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        # Priority dropdown
        ttk.Label(frame, text="Priority:", font=("Arial", 12, "bold")).grid(
            row=5, column=0, sticky="w", padx=5, pady=5)
        priority_options = ["Critical", "High", "Medium", "Low"]
        self.priority_combo = ttk.Combobox(frame, values=priority_options, state="readonly")
        self.priority_combo.set(priority)
        self.priority_combo.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        # Assigned User dropdown
        ttk.Label(frame, text="Assigned User:", font=("Arial", 12, "bold")).grid(
            row=6, column=0, sticky="w", padx=5, pady=5)
        self.user_combo = ttk.Combobox(frame, state="readonly")
        # Populate the user dropdown with the team members.
        team_members = self.controller.trasker.list_team_members()  # Should return list of (user_id, username)
        self.user_map = {member[1]: member[0] for member in team_members}
        user_options = list(self.user_map.keys())
        if user_options:
            self.user_combo['values'] = user_options
            current_username = self.controller.trasker.get_username(current_user_id) if current_user_id else ""
            if current_username in user_options:
                self.user_combo.set(current_username)
            else:
                self.user_combo.current(0)
        else:
            self.user_combo['values'] = []
        self.user_combo.grid(row=6, column=1, sticky="ew", padx=5, pady=5)

        # Team dropdown
        ttk.Label(frame, text="Team:", font=("Arial", 12, "bold")).grid(
            row=7, column=0, sticky="w", padx=5, pady=5)
        self.team_combo = ttk.Combobox(frame, state="readonly")
        # Populate the team dropdown with teams available to the current user.
        teams = self.controller.trasker.list_user_teams()  # Should return list of (team_id, team_name)
        self.team_map = {team[1]: team[0] for team in teams}
        team_options = list(self.team_map.keys())
        if team_options:
            self.team_combo['values'] = team_options
            current_team_name = self.controller.trasker.get_team_name(current_team_id) if current_team_id else ""
            if current_team_name in team_options:
                self.team_combo.set(current_team_name)
            else:
                self.team_combo.current(0)
        else:
            self.team_combo['values'] = []
        self.team_combo.grid(row=7, column=1, sticky="ew", padx=5, pady=5)

        # Configure column weights.
        frame.columnconfigure(1, weight=1)

        # Save button.
        ttk.Button(frame, text="Save Changes", command=self.save_edits).grid(
            row=8, column=0, columnspan=2, pady=10)

    def save_edits(self):
        new_title = self.title_entry.get().strip()
        new_description = self.description_text.get("1.0", "end").strip()
        new_due_date = self.due_date_entry.get().strip()
        new_status = self.status_combo.get().strip()
        new_category = self.category_entry.get().strip()
        new_priority = self.priority_combo.get().strip()

        # Retrieve selected user and team names.
        new_user_name = self.user_combo.get().strip()
        new_team_name = self.team_combo.get().strip()

        # Convert names to IDs using helper methods.
        new_user_id = self.controller.trasker.get_user_id_from_username(new_user_name)
        new_team_id = self.controller.trasker.get_team_id_from_teamname(new_team_name)

        # Update the basic task fields.
        self.controller.trasker.task_change_title(self.task_id, new_title)
        self.controller.trasker.task_change_description(self.task_id, new_description)
        self.controller.trasker.task_change_status(self.task_id, new_status)
        self.controller.trasker.task_change_category(self.task_id, new_category)
        self.controller.trasker.task_change_priority(self.task_id, new_priority)

        # Update the assigned user and team.
        self.controller.trasker.task_change_assignee(self.task_id, new_user_id, new_team_id)

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
