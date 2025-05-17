# trasker_gui/single_task_view.py
import tkinter as tk
from tkinter import ttk, messagebox


class SingleTaskView(tk.Toplevel):
    def __init__(self, parent, controller, task_id, refresh_callback=None):
        """
        Opens a window displaying detailed information about a task.
        Displays multi-user information such as the creator’s username and team name.

        parent: the master widget (e.g. TaskView or BoardView)
        controller: the main controller (TraskerGUI instance)
        task_id: the ID of the task to display
        refresh_callback: a callable to refresh the calling view when needed
        """
        super().__init__(parent)
        self.controller = controller
        self.task_id = task_id
        self.refresh_callback = refresh_callback
        self.title("Task Details")
        self.geometry("1800x900")

        # Create a main frame with padding.
        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Retrieve the task details.
        # list_task_by_id() is expected to return a list with one tuple.
        task = self.controller.trasker.list_task_by_id(task_id)
        if not task:
            messagebox.showerror("Error", "Task not found!")
            self.destroy()
            return

        # Unpack the task tuple.
        # Expected tuple format:
        # (id, title, description, due_date, status, category, priority, timer, user_id, team_id)
        task_id, title, description, due_date, status, category, priority, timer, user_id, team_id = task

        # Get user and team display names via helper methods.
        user_name = self.controller.trasker.get_username(user_id) if user_id else "N/A"
        team_name = self.controller.trasker.get_team_name(team_id) if team_id else "N/A"

        # Create labels to display task details.
        ttk.Label(frame, text="Title:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=title).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="nw", padx=5,
                                                                               pady=5)
        desc_text = tk.Text(frame, height=10, wrap="word")
        desc_text.insert("1.0", description)
        desc_text.configure(state="disabled")
        desc_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Due Date:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=due_date).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Status:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=status).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Category:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=category).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Priority:", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=priority).grid(row=5, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Timer:", font=("Arial", 12, "bold")).grid(row=6, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=str(timer)).grid(row=6, column=1, sticky="w", padx=5, pady=5)

        # Display multi-user fields.
        ttk.Label(frame, text="Created by:", font=("Arial", 12, "bold")).grid(row=7, column=0, sticky="w", padx=5,
                                                                              pady=5)
        ttk.Label(frame, text=user_name).grid(row=7, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Team:", font=("Arial", 12, "bold")).grid(row=8, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text=team_name).grid(row=8, column=1, sticky="w", padx=5, pady=5)

        # Related Bugs Section.
        ttk.Label(frame, text="Related Bugs:", font=("Arial", 12, "bold")).grid(row=9, column=0, sticky="w", padx=5,
                                                                                pady=(10, 0))
        bugs = self.controller.trasker.list_bugs_by_task(task_id)
        if bugs:
            row_index = 10
            for bug in bugs:
                bug_title = bug[1]
                bug_status = bug[3]
                bug_created = bug[4]
                bug_summary = f"{bug_title} (Status: {bug_status}, Created: {bug_created})"
                ttk.Label(frame, text=bug_summary, wraplength=500).grid(row=row_index, column=0, columnspan=2,
                                                                        sticky="w", padx=5, pady=2)
                row_index += 1
        else:
            ttk.Label(frame, text="No related bugs found.", font=("Arial", 10, "italic")).grid(row=10, column=0,
                                                                                               columnspan=2, sticky="w",
                                                                                               padx=5, pady=(5, 0))

        # Button to open the Edit Task view.
        ttk.Button(frame, text="Edit Task", command=self.open_edit_view).grid(row=row_index + 1, column=0, columnspan=2,
                                                                              pady=10)

    def open_edit_view(self):
        from trasker_gui.supporting_view.edit_task_view import EditTaskView
        EditTaskView(self, self.controller, self.task_id, refresh_callback=self.refresh_view)

    def refresh_view(self):
        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
