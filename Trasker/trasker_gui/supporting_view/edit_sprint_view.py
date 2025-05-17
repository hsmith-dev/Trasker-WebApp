import tkinter as tk
from tkinter import ttk, messagebox

class EditSprintView(tk.Toplevel):
    def __init__(self, parent, controller, sprint_id, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.sprint_id = sprint_id
        self.refresh_callback = refresh_callback

        self.title("Edit Sprint")
        self.geometry("600x500")

        # Retrieve sprint details.
        sprint = self.controller.trasker.list_sprint_by_id(sprint_id)
        if not sprint:
            messagebox.showerror("Error", "Sprint not found!")
            self.destroy()
            return

        # Expected sprint tuple: (id, title, description, start_date, end_date, epic_id, user_id, team_id)
        # (Depending on your implementation, the tuple may have more fields.)
        _, title, description, start_date, end_date, epic_id, *_ = sprint

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

        # Description
        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(frame, height=8, width=50, wrap="word")
        self.description_text.insert("1.0", description)
        self.description_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Start Date
        ttk.Label(frame, text="Start Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky="w", padx=5, pady=5)
        self.start_date_entry = ttk.Entry(frame)
        self.start_date_entry.insert(0, start_date)
        self.start_date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # End Date
        ttk.Label(frame, text="End Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(
            row=3, column=0, sticky="w", padx=5, pady=5)
        self.end_date_entry = ttk.Entry(frame)
        self.end_date_entry.insert(0, end_date)
        self.end_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Epic dropdown (to link this sprint with an epic)
        ttk.Label(frame, text="Epic:", font=("Arial", 12, "bold")).grid(
            row=4, column=0, sticky="w", padx=5, pady=5)
        epics = self.controller.trasker.list_epics()
        epic_options = [epic[1] for epic in epics]
        self.epic_combo = ttk.Combobox(frame, values=epic_options, state="readonly")
        current_epic = next((epic[1] for epic in epics if epic[0] == epic_id), "")
        self.epic_combo.set(current_epic)
        self.epic_combo.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Save Changes", command=self.save_edits).grid(
            row=5, column=0, columnspan=2, pady=10)

    def save_edits(self):
        new_title = self.title_entry.get().strip()
        new_description = self.description_text.get("1.0", "end").strip()
        new_start_date = self.start_date_entry.get().strip()
        new_end_date = self.end_date_entry.get().strip()
        new_epic_name = self.epic_combo.get().strip()

        # Retrieve the epic ID from the selected epic name.
        epics = self.controller.trasker.list_epics()
        new_epic_id = next((epic[0] for epic in epics if epic[1] == new_epic_name), None)

        try:
            self.controller.trasker.edit_sprint(self.sprint_id, new_title, new_description, new_start_date, new_end_date, epic_id=new_epic_id)
            messagebox.showinfo("Success", "Sprint updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update sprint: {e}")
            return

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
