import tkinter as tk
from tkinter import ttk, messagebox

class AddSprintView(tk.Toplevel):
    def __init__(self, parent, controller, refresh_callback):
        super().__init__(parent)
        self.controller = controller
        self.refresh_callback = refresh_callback

        self.title("Add Sprint")
        self.geometry("600x500")

        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        ttk.Label(frame, text="Title:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ttk.Entry(frame)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Description
        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(frame, height=8, width=50, wrap="word")
        self.description_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Start Date
        ttk.Label(frame, text="Start Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky="w", padx=5, pady=5)
        self.start_date_entry = ttk.Entry(frame)
        self.start_date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # End Date
        ttk.Label(frame, text="End Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(
            row=3, column=0, sticky="w", padx=5, pady=5)
        self.end_date_entry = ttk.Entry(frame)
        self.end_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Epic dropdown (to link this sprint with an epic)
        ttk.Label(frame, text="Epic:", font=("Arial", 12, "bold")).grid(
            row=4, column=0, sticky="w", padx=5, pady=5)
        # Get epic options from the Trasker instance.
        epics = self.controller.trasker.list_epics()
        epic_options = [epic[1] for epic in epics]
        self.epic_combo = ttk.Combobox(frame, values=epic_options, state="readonly")
        if epic_options:
            self.epic_combo.set(epic_options[0])
        self.epic_combo.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Add Sprint", command=self.submit_sprint).grid(
            row=5, column=0, columnspan=2, pady=10)

    def submit_sprint(self):
        title = self.title_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        epic_name = self.epic_combo.get().strip()

        if not title or not start_date or not end_date:
            messagebox.showerror("Error", "Title, Start Date, and End Date are required!")
            return

        # Retrieve the epic id from the epic name.
        epics = self.controller.trasker.list_epics()
        epic_id = next((epic[0] for epic in epics if epic[1] == epic_name), None)

        try:
            # Create sprint using the multi-user method; current user/team are set internally.
            self.controller.trasker.create_sprint(title, description, start_date, end_date, epic_id=epic_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add sprint: {e}")
            return

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
