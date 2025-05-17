import sys
import tkinter as tk
from tkinter import ttk, messagebox
from trasker_gui.supporting_view.single_task_view import SingleTaskView
from trasker_gui.supporting_view.edit_task_view import EditTaskView

class BoardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Filter Panel ---
        filter_panel = ttk.Frame(self)
        filter_panel.pack(fill=tk.X, pady=5)

        # Team filter combobox
        ttk.Label(filter_panel, text="Filter by Team:").pack(side=tk.LEFT, padx=5)
        self.team_filter = ttk.Combobox(filter_panel, state="readonly")
        self.team_filter.pack(side=tk.LEFT, padx=5)
        self.team_filter.bind("<<ComboboxSelected>>", self.refresh_board)

        # User filter combobox
        ttk.Label(filter_panel, text="Filter by User:").pack(side=tk.LEFT, padx=5)
        self.user_filter = ttk.Combobox(filter_panel, state="readonly")
        self.user_filter.pack(side=tk.LEFT, padx=5)
        self.user_filter.bind("<<ComboboxSelected>>", self.refresh_board)

        # Epic filter combobox
        ttk.Label(filter_panel, text="Filter by Epic:").pack(side=tk.LEFT, padx=5)
        self.epic_filter = ttk.Combobox(filter_panel, state="readonly")
        self.epic_filter.pack(side=tk.LEFT, padx=5)
        self.epic_filter.bind("<<ComboboxSelected>>", self.refresh_board)

        # Sprint filter combobox
        ttk.Label(filter_panel, text="Filter by Sprint:").pack(side=tk.LEFT, padx=5)
        self.sprint_filter = ttk.Combobox(filter_panel, state="readonly")
        self.sprint_filter.pack(side=tk.LEFT, padx=5)
        self.sprint_filter.bind("<<ComboboxSelected>>", self.refresh_board)

        self.load_epic_dropdown()
        self.load_sprint_dropdown()
        self.load_user_dropdown()
        self.load_team_dropdown()

        # --- Board Columns ---
        self.columns_frame = ttk.Frame(self)
        self.columns_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define board statuses (adjust these to match your task status values)
        self.board_statuses = ["Holding", "Pending", "In Progress", "Completed"]
        self.columns = {}

        # Create one column per status
        for status in self.board_statuses:
            col_frame = ttk.Frame(self.columns_frame, borderwidth=2, relief="groove")
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            title_label = ttk.Label(col_frame, text=status, font=("Arial", 14, "bold"))
            title_label.pack(pady=5)
            # Use a plain tk.Frame for the container to allow free positioning during drag and drop
            tasks_container = ttk.Frame(col_frame)
            tasks_container.pack(fill=tk.BOTH, expand=True)
            self.columns[status] = tasks_container

        # Initialize drag data dictionary and load tasks
        self.drag_data = {}
        self.refresh_board()

    def load_epic_dropdown(self):
        """Populate the epic filter combobox."""
        epics = self.controller.trasker.list_epics()
        epic_names = ["All Epics"] + [epic[1] for epic in epics]
        self.epic_filter["values"] = epic_names
        self.epic_filter.current(0)

    def load_sprint_dropdown(self, sprints=None):
        """Populate the sprint filter combobox."""
        if sprints is None:
            sprints = self.controller.trasker.list_sprints()
        sprint_names = ["All Sprints"] + [sprint[1] for sprint in sprints]
        self.sprint_filter["values"] = sprint_names
        self.sprint_filter.current(0)

    def load_user_dropdown(self):
        """Load team members into the user filter combobox."""
        # We assume the current team is stored in self.controller.trasker.current_team.
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
            user_names = ["All Users"] + [row[1] for row in rows]
            self.user_filter["values"] = user_names
            self.user_filter.current(0)
        else:
            self.user_filter["values"] = ["All Users"]
            self.user_filter.current(0)

    def load_team_dropdown(self):
        """Load teams that the current user belongs to into the team filter combobox."""
        # We assume the current user's id is stored in self.controller.current_user.
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            # If current_user is a tuple (e.g. (id, username, ...)), extract the id.
            current_user = self.controller.current_user
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

    def refresh_board(self, event=None):
        """Reload board tasks based on current filters."""
        self.load_board_tasks()

    def load_board_tasks(self):
        """Clear and repopulate board columns with tasks filtered by epic, sprint, user, and team."""
        # Clear existing tasks from each column.
        for container in self.columns.values():
            for widget in container.winfo_children():
                widget.destroy()

        tasks = self.controller.trasker.list_all_tasks()
        epic_filter = self.epic_filter.get()
        sprint_filter = self.sprint_filter.get()
        user_filter_value = self.user_filter.get()
        team_filter_value = self.team_filter.get()

        filtered_tasks = tasks

        # Epic filtering.
        if epic_filter != "All Epics":
            epics = self.controller.trasker.list_epics()
            epic_id = next((epic[0] for epic in epics if epic[1] == epic_filter), None)
            if epic_id:
                filtered_tasks = [task for task in filtered_tasks if self._task_belongs_to_epic(task, epic_id)]
            else:
                filtered_tasks = []

        # Sprint filtering.
        if sprint_filter != "All Sprints":
            sprints = self.controller.trasker.list_sprints()
            sprint_id = next((sprint[0] for sprint in sprints if sprint[1] == sprint_filter), None)
            if sprint_id:
                # Assuming sprint_id is at index 9 in the task tuple.
                filtered_tasks = [task for task in filtered_tasks if task[9] == sprint_id]
            else:
                filtered_tasks = []

        # User filtering.
        if user_filter_value != "All Users":
            # Assuming user_id is at index 10 in the task tuple.
            filtered_tasks = [task for task in filtered_tasks
                              if task[10] == user_filter_value]

        # Team filtering.
        if team_filter_value != "All Teams":
            # Use our team_map to look up the team_id based on team name.

            team_id = self.team_map.get(team_filter_value)
            if team_id is not None:
                # Assuming team_id is at index 11 in the task tuple.
                filtered_tasks = [task for task in filtered_tasks if task[11] == team_filter_value]
            else:
                filtered_tasks = []

        # Distribute tasks into columns by status.
        for task in filtered_tasks:
            task_id = task[0]
            status = task[4] if task[4] in self.board_statuses else "Holding"
            container = self.columns.get(status, self.columns["Holding"])
            task_widget = ttk.Label(container, text=task[1], relief="raised", padding=5)
            task_widget.pack(pady=5, padx=5, fill=tk.X)
            # Bind events with lambda so that the task id is passed.
            task_widget.bind("<ButtonPress-1>",
                             lambda event, t_id=task_id, w=task_widget: self.on_task_press(event, t_id, w))
            task_widget.bind("<B1-Motion>", self.on_task_drag)
            task_widget.bind("<ButtonRelease-1>",
                             lambda event, t_id=task_id: self.on_task_drop(event, t_id))
            # Bind right-click to show context menu (using Control-Button-1 on macOS).
            if sys.platform == "darwin":
                task_widget.bind("<Control-Button-1>",
                                 lambda event, t_id=task_id: self.show_task_context_menu(event, t_id))
                task_widget.bind("<Button-2>",
                                 lambda event, t_id=task_id: self.show_task_context_menu(event, t_id))
            else:
                task_widget.bind("<Button-3>",
                                 lambda event, t_id=task_id: self.show_task_context_menu(event, t_id))

    def _task_belongs_to_epic(self, task, epic_id):
        """Return True if the task belongs to the given epic via its sprint."""
        sprint_id = task[9]
        if sprint_id is None:
            return False
        sprint = self.controller.trasker.get_sprint_by_id(sprint_id)
        if sprint and sprint[5] == epic_id:
            return True
        return False

    def on_task_press(self, event, task_id, orig_widget):
        """Create a floating copy of the task widget for dragging."""
        self.drag_data = {"widget": orig_widget, "x": event.x, "y": event.y, "task_id": task_id}
        self.floating = tk.Label(self, text=orig_widget.cget("text"), relief="raised", bg="lightgray")
        x = event.x_root - self.winfo_rootx()
        y = event.y_root - self.winfo_rooty()
        self.floating.place(x=x, y=y)
        orig_widget.configure(foreground="gray")

    def on_task_drag(self, event):
        """Move the floating widget to follow the mouse pointer."""
        if hasattr(self, "floating") and self.floating:
            x = event.x_root - self.winfo_rootx()
            y = event.y_root - self.winfo_rooty()
            self.floating.place(x=x, y=y)

    def on_task_drop(self, event, task_id):
        """Determine the target column and update the task's status on drop."""
        self.update_idletasks()
        drop_x = event.x_root
        drop_y = event.y_root
        target_status = None
        for status, container in self.columns.items():
            cont_x = container.winfo_rootx()
            cont_y = container.winfo_rooty()
            cont_width = container.winfo_width()
            cont_height = container.winfo_height()
            if (drop_x >= cont_x and drop_x <= cont_x + cont_width and
                    drop_y >= cont_y and drop_y <= cont_y + cont_height):
                target_status = status
                break
        if "widget" in self.drag_data:
            self.drag_data["widget"].configure(foreground="black")
        if hasattr(self, "floating") and self.floating:
            self.floating.destroy()
            self.floating = None
            self.drag_data = {}
        if target_status is not None:
            self.controller.trasker.task_change_status(task_id, target_status)
        else:
            messagebox.showinfo("Drop", "Task was not dropped in a valid column. No status update performed.")
        self.load_board_tasks()

    def show_task_context_menu(self, event, task_id):
        """Show a right-click context menu for a task."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="View Task", command=lambda: self.view_task(task_id))
        menu.add_command(label="Edit Task", command=lambda: self.edit_task(task_id))
        menu.add_command(label="Archive Task", command=lambda: self.archive_task(task_id))
        menu.add_command(label="Delete Task", command=lambda: self.delete_task(task_id))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def view_task(self, task_id):
        SingleTaskView(self, self.controller, task_id, refresh_callback=self.refresh_board)

    def edit_task(self, task_id):
        EditTaskView(self, self.controller, task_id, refresh_callback=self.refresh_board)

    def archive_task(self, task_id):
        self.controller.trasker.task_mark_archived(task_id)
        self.refresh_board()

    def delete_task(self, task_id):
        self.controller.trasker.delete_task(task_id)
        self.refresh_board()
