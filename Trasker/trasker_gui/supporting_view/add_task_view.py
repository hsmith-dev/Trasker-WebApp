import tkinter as tk
from tkinter import ttk, messagebox

class AddTaskView(tk.Toplevel):
    def __init__(self, parent, controller, refresh_callback):
        """
        parent: the master widget (typically TaskView or BoardView)
        controller: the main controller (TraskerGUI instance) that holds the Trasker logic
        refresh_callback: a function to refresh the tasks list after adding
        """
        super().__init__(parent)
        self.controller = controller
        self.refresh_callback = refresh_callback
        self.title("Add Task")
        self.geometry("1800x900")

        # Create a frame with padding and grid layout.
        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        ttk.Label(frame, text="Title:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ttk.Entry(frame)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Description (multi-line)
        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(frame, height=10, width=50, wrap="word")
        self.description_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Due Date
        ttk.Label(frame, text="Due Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky="w", padx=5, pady=5)
        self.due_date_entry = ttk.Entry(frame)
        self.due_date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Category
        ttk.Label(frame, text="Category:", font=("Arial", 12, "bold")).grid(
            row=3, column=0, sticky="w", padx=5, pady=5)
        self.category_entry = ttk.Entry(frame)
        self.category_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Status dropdown
        ttk.Label(frame, text="Status:", font=("Arial", 12, "bold")).grid(
            row=4, column=0, sticky="w", padx=5, pady=5)
        status_options = ["Holding", "Pending", "In Progress", "Completed", "Archived"]
        self.status_combo = ttk.Combobox(frame, values=status_options, state="readonly")
        self.status_combo.set("Pending")  # Default
        self.status_combo.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        # Priority dropdown
        ttk.Label(frame, text="Priority:", font=("Arial", 12, "bold")).grid(
            row=5, column=0, sticky="w", padx=5, pady=5)
        priority_options = ["Critical", "High", "Medium", "Low"]
        self.priority_combo = ttk.Combobox(frame, values=priority_options, state="readonly")
        self.priority_combo.set("Medium")  # Default
        self.priority_combo.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Add Task", command=self.submit_task).grid(
            row=6, column=0, columnspan=2, pady=10)

    def submit_task(self):
        title = self.title_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        due_date = self.due_date_entry.get().strip()
        category = self.category_entry.get().strip() or "General"
        status = self.status_combo.get().strip()
        priority = self.priority_combo.get().strip()

        if not title or not due_date:
            messagebox.showerror("Error", "Title and Due Date are required!")
            return

        try:
            # The Trasker.add_task method now automatically includes multi-user context.
            self.controller.trasker.add_task(
                title, description, due_date,
                status=status, category=category, priority=priority
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add task: {e}")
            return

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
