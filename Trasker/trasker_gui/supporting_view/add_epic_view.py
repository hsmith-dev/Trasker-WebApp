import tkinter as tk
from tkinter import ttk, messagebox

class AddEpicView(tk.Toplevel):
    def __init__(self, parent, controller, refresh_callback):
        """
        parent: calling widget (e.g. EpicView)
        controller: main controller (TraskerGUI) holding the Trasker instance
        refresh_callback: callable to refresh the epic list after adding
        """
        super().__init__(parent)
        self.controller = controller
        self.refresh_callback = refresh_callback

        self.title("Add Epic")
        self.geometry("600x400")

        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Epic Name
        ttk.Label(frame, text="Name:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Description (multi‑line)
        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(frame, height=6, width=50, wrap="word")
        self.description_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Start Date
        ttk.Label(frame, text="Start Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.start_date_entry = ttk.Entry(frame)
        self.start_date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # End Date
        ttk.Label(frame, text="End Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.end_date_entry = ttk.Entry(frame)
        self.end_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Add Epic", command=self.submit_epic).grid(row=4, column=0, columnspan=2, pady=10)

    def submit_epic(self):
        name = self.name_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()

        if not name or not start_date or not end_date:
            messagebox.showerror("Error", "Name, Start Date, and End Date are required!")
            return

        # Retrieve the current user and team from the Trasker instance.
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

        # Create the epic with the additional user and team information.
        try:
            self.controller.trasker.create_epic(name, description, start_date, end_date, user_id, team_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add epic: {e}")
            return

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
import tkinter as tk
from tkinter import ttk, messagebox

class AddEpicView(tk.Toplevel):
    def __init__(self, parent, controller, refresh_callback):
        """
        parent: calling widget (e.g. EpicView)
        controller: main controller (TraskerGUI) holding the Trasker instance
        refresh_callback: callable to refresh the epic list after adding
        """
        super().__init__(parent)
        self.controller = controller
        self.refresh_callback = refresh_callback

        self.title("Add Epic")
        self.geometry("600x400")

        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Epic Name
        ttk.Label(frame, text="Name:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Description (multi‑line)
        ttk.Label(frame, text="Description:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(frame, height=6, width=50, wrap="word")
        self.description_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Start Date
        ttk.Label(frame, text="Start Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.start_date_entry = ttk.Entry(frame)
        self.start_date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # End Date
        ttk.Label(frame, text="End Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.end_date_entry = ttk.Entry(frame)
        self.end_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Add Epic", command=self.submit_epic).grid(row=4, column=0, columnspan=2, pady=10)

    def submit_epic(self):
        name = self.name_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()

        if not name or not start_date or not end_date:
            messagebox.showerror("Error", "Name, Start Date, and End Date are required!")
            return

        # Retrieve the current user and team from the Trasker instance.
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

        # Create the epic with the additional user and team information.
        try:
            self.controller.trasker.create_epic(name, description, start_date, end_date, user_id, team_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add epic: {e}")
            return

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
