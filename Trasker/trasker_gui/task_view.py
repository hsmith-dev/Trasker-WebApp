import tkinter as tk
from tkinter import ttk, messagebox
from trasker_gui.supporting_view.add_task_view import AddTaskView
from datetime import datetime

class TaskView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Reference to the main controller (TraskerGUI)

        # TOP PANEL: Filters (User, and Team)
        filter_panel = ttk.Frame(self)
        filter_panel.pack(fill=tk.X, pady=5)

        # TOP PANEL 2: Filters (Epic, Sprint, Status, Date Range)
        filter_panel_2 = ttk.Frame(self)
        filter_panel_2.pack(fill=tk.X, pady=5)

        # Team filter combobox
        ttk.Label(filter_panel, text="Filter by Team:").pack(side=tk.LEFT, padx=5)
        self.team_filter = ttk.Combobox(filter_panel, state="readonly")
        self.team_filter.pack(side=tk.LEFT, padx=5)
        self.team_filter.bind("<<ComboboxSelected>>", self.filter_tasks)

        # User filter combobox
        ttk.Label(filter_panel, text="Filter by User:").pack(side=tk.LEFT, padx=5)
        self.user_filter = ttk.Combobox(filter_panel, state="readonly")
        self.user_filter.pack(side=tk.LEFT, padx=5)
        self.user_filter.bind("<<ComboboxSelected>>", self.filter_tasks)

        # Epic filter combobox
        ttk.Label(filter_panel_2, text="Filter by Epic:").pack(side=tk.LEFT, padx=5)
        self.epic_filter = ttk.Combobox(filter_panel_2, state="readonly")
        self.epic_filter.pack(side=tk.LEFT, padx=5)
        self.epic_filter.bind("<<ComboboxSelected>>", self.epic_filter_changed)

        # Sprint filter combobox
        ttk.Label(filter_panel_2, text="Filter by Sprint:").pack(side=tk.LEFT, padx=5)
        self.sprint_filter = ttk.Combobox(filter_panel_2, state="readonly")
        self.sprint_filter.pack(side=tk.LEFT, padx=5)
        self.sprint_filter.bind("<<ComboboxSelected>>", self.filter_tasks)

        # Status filter combobox
        ttk.Label(filter_panel_2, text="Filter by Status:").pack(side=tk.LEFT, padx=5)
        self.status_filter = ttk.Combobox(filter_panel_2, state="readonly")
        self.status_filter.pack(side=tk.LEFT, padx=5)
        self.status_filter.bind("<<ComboboxSelected>>", self.filter_tasks)

        # Date range filter for Due Dates
        ttk.Label(filter_panel_2, text="Due Date From (YYYY-MM-DD):").pack(side=tk.LEFT, padx=5)
        self.from_date_entry = ttk.Entry(filter_panel_2, width=12)
        self.from_date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_panel_2, text="To:").pack(side=tk.LEFT, padx=5)
        self.to_date_entry = ttk.Entry(filter_panel_2, width=12)
        self.to_date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_panel_2, text="Apply Date Filter", command=self.filter_tasks).pack(side=tk.LEFT, padx=5)

        # Populate the static comboboxes.
        self.load_epic_dropdown()
        self.load_sprint_dropdown()
        self.load_status_dropdown()
        self.load_user_dropdown()
        self.load_team_dropdown()

        # MAIN CONTAINER for the task view.
        main_frame = ttk.Frame(self)
        main_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # LEFT PANEL: Task controls.
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Button(left_panel, text="+ Add Task", command=self.show_add_task_window, width=20).pack(pady=5)
        ttk.Label(left_panel, text="⏱️ Task Timer", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Button(left_panel, text="▶️ Start", command=self.start_task_timer, width=20).pack(pady=5)
        ttk.Button(left_panel, text="🛑 Stop", command=self.stop_task_timer, width=20).pack(pady=5)
        ttk.Label(left_panel, text="🕹️ Task Controls", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Button(left_panel, text="🔍 View", command=self.show_task_details, width=20).pack(pady=5)
        ttk.Button(left_panel, text="✅ Complete", command=self.complete_task, width=20).pack(pady=5)
        ttk.Button(left_panel, text="📂 Archive", command=self.archive_task, width=20).pack(pady=5)
        ttk.Button(left_panel, text="🗑️ Delete", command=self.delete_task, width=20).pack(pady=5)

        # RIGHT PANEL: Task table.
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Treeview", rowheight=50)

        # Include columns for ID, Title, Description, Due Date, Status, Category, Priority, User, Team, Timer.
        columns = ("ID", "Title", "Description", "Due Date", "Status", "Category", "Priority", "User", "Team", "Timer")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", lambda event: self.show_task_details())

        # Load tasks on initialization.
        self.load_tasks()

    def load_epic_dropdown(self):
        epics = self.controller.trasker.list_epics()
        epic_names = ["All Epics"] + [epic[1] for epic in epics]
        self.epic_filter['values'] = epic_names
        self.epic_filter.current(0)

    def load_sprint_dropdown(self, sprints=None):
        if sprints is None:
            sprints = self.controller.trasker.list_sprints()
        sprint_names = ["All Sprints"] + [sprint[1] for sprint in sprints]
        self.sprint_filter['values'] = sprint_names
        self.sprint_filter.current(0)

    def load_status_dropdown(self):
        statuses = ["All Statuses", "Holding", "Pending", "In Progress", "Completed", "Archived"]
        self.status_filter['values'] = statuses
        self.status_filter.current(0)

    def load_user_dropdown(self):
        """Load users (team members) into the user filter combobox."""
        if hasattr(self.controller.trasker, "current_user") and self.controller.trasker.current_user:
            current_user = self.controller.trasker.current_user
            if isinstance(current_user, tuple):
                current_user_id = current_user[0]
            else:
                current_user_id = current_user
            # Retrieve users from teams that current user is a member of.
            query = """
                SELECT u.id, u.username
                FROM users u
                JOIN user_team ut ON u.id = ut.user_id
                WHERE ut.team_id IN (
                    SELECT team_id FROM user_team WHERE user_id = %s
                )
            """
            rows = self.controller.trasker.db_execute(query, (current_user_id,), fetch=True)
            user_names = ["All Users"]
            self.user_map = {}
            for row in rows:
                user_id, username = row
                user_names.append(username)
                self.user_map[username] = user_id
            self.user_filter['values'] = user_names
            self.user_filter.current(0)
        else:
            self.user_filter['values'] = ["All Users"]
            self.user_filter.current(0)

    def load_team_dropdown(self):
        """Load teams that the current user belongs to into the team filter combobox."""
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
            self.team_filter['values'] = team_names
            self.team_filter.current(0)
        else:
            self.team_filter['values'] = ["All Teams"]
            self.team_filter.current(0)

    def load_tasks(self):
        """Load tasks (using the filter criteria) into the treeview."""
        self.filter_tasks()

    def filter_tasks(self, event=None):
        # Retrieve all tasks from the core logic.
        tasks = self.controller.trasker.list_all_tasks()
        filtered_tasks = tasks

        # Apply due date range filtering.
        from_date_str = self.from_date_entry.get().strip()
        to_date_str = self.to_date_entry.get().strip()
        if from_date_str or to_date_str:
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d") if from_date_str else None
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d") if to_date_str else None
            except ValueError:
                messagebox.showerror("Error", "Due date filters must be in YYYY-MM-DD format")
                return
            temp_tasks = []
            for task in filtered_tasks:
                try:
                    due_date = datetime.strptime(task[3], "%Y-%m-%d")
                except ValueError:
                    continue
                if from_date and to_date:
                    if from_date <= due_date <= to_date:
                        temp_tasks.append(task)
                elif from_date and due_date >= from_date:
                    temp_tasks.append(task)
                elif to_date and due_date <= to_date:
                    temp_tasks.append(task)
            filtered_tasks = temp_tasks

        # Epic filtering.
        selected_epic = self.epic_filter.get()
        if selected_epic != "All Epics":
            epics = self.controller.trasker.list_epics()
            epic_ids = [epic[0] for epic in epics if epic[1] == selected_epic]
            # Here, we assume the sprint (which links to epic) is at index 9.
            filtered_tasks = [task for task in filtered_tasks if task[9] in epic_ids]

        # Sprint filtering.
        selected_sprint = self.sprint_filter.get()
        if selected_sprint != "All Sprints":
            sprints = self.controller.trasker.list_sprints()
            sprint_ids = [sprint[0] for sprint in sprints if sprint[1] == selected_sprint]
            filtered_tasks = [task for task in filtered_tasks if task[9] in sprint_ids]

        # Status filtering.
        selected_status = self.status_filter.get()
        if selected_status != "All Statuses":
            filtered_tasks = [task for task in filtered_tasks if task[4] == selected_status]

        # Team filtering.
        selected_team = self.team_filter.get()
        if selected_team != "All Teams":
            filtered_tasks = [task for task in filtered_tasks if task[11] == selected_team]

        # User filtering.
        selected_user = self.user_filter.get()
        if selected_user != "All Users":
            filtered_tasks = [task for task in filtered_tasks if task[10] == selected_user]

        # Clear the treeview and insert filtered tasks.
        for row in self.tree.get_children():
            self.tree.delete(row)
        for task in filtered_tasks:
            task_id = task[0]
            timer_value = "running" if self.controller.trasker.is_timer_running(task_id) else self.controller.trasker.get_total_task_time(task_id)
            # Convert user_id and team_id into names using our maps.
            username = task[10]
            teamname = task[11]
            values = (task[0], task[1], task[2], task[3], task[4], task[5], task[6], username, teamname, timer_value)
            self.tree.insert("", tk.END, values=values)

    def epic_filter_changed(self, event=None):
        selected_epic = self.epic_filter.get()
        if selected_epic == "All Epics":
            self.load_sprint_dropdown()
        else:
            epics = self.controller.trasker.list_epics()
            epic_id = next((epic[0] for epic in epics if epic[1] == selected_epic), None)
            if epic_id:
                all_sprints = self.controller.trasker.list_sprints()
                filtered_sprints = [sprint for sprint in all_sprints if sprint[5] == epic_id]
                self.load_sprint_dropdown(filtered_sprints)
            else:
                self.load_sprint_dropdown([])
        self.filter_tasks()

    def show_add_task_window(self):
        AddTaskView(self, self.controller, refresh_callback=self.load_tasks)

    def show_task_details(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return
        task_values = self.tree.item(selected[0], "values")
        if not task_values:
            return
        task_id = task_values[0]
        print("Task id:", task_id)  # Debug
        from trasker_gui.supporting_view.single_task_view import SingleTaskView
        SingleTaskView(self, self.controller, task_id, refresh_callback=self.load_tasks)

    def complete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return
        task_id = self.tree.item(selected[0], "values")[0]
        self.controller.trasker.task_mark_completed(task_id)
        self.load_tasks()

    def archive_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return
        task_id = self.tree.item(selected[0], "values")[0]
        self.controller.trasker.task_mark_archived(task_id)
        self.load_tasks()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return
        if messagebox.askyesno("Delete", "Do you want to delete the selected task%s"):
            task_id = self.tree.item(selected[0], "values")[0]
            self.controller.trasker.delete_task(task_id)
            self.load_tasks()

    def start_task_timer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return
        task_id = self.tree.item(selected[0], "values")[0]
        self.controller.trasker.start_task_timer(task_id)
        messagebox.showinfo("Timer Started", f"Timer started for task {task_id}")

    def stop_task_timer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return
        task_id = self.tree.item(selected[0], "values")[0]
        self.controller.trasker.stop_task_timer(task_id)
        elapsed_time = self.controller.trasker.get_total_task_time(task_id)
        messagebox.showinfo("Timer Stopped", f"Total time spent on Task {task_id}: {elapsed_time} seconds")
