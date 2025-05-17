import configparser
import os
import tkinter as tk
from tkinter import ttk, messagebox
from trasker_psql import Trasker
from trasker_gui.home_view import HomeView
from trasker_gui.epic_view import EpicView
from trasker_gui.sprint_view import SprintView
from trasker_gui.board_view import BoardView
from trasker_gui.task_view import TaskView
from trasker_gui.bug_view import BugView
from trasker_gui.notes_view import NotesView
from trasker_gui.documents_view import DocumentsView
from trasker_gui.setting_view import SettingView
from trasker_gui.admin_view import AdminView


class LoginDialog(tk.Toplevel):
    def __init__(self, parent, trasker):
        super().__init__(parent)
        self.trasker = trasker
        self.title("Login")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Username:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Password:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        login_btn = ttk.Button(frame, text="Login", command=self.attempt_login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.result = None

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        user_id = self.trasker.verify_user(username, password)
        if user_id is None:
            messagebox.showerror("Error", "Invalid username or password.")
        else:
            self.result = user_id
            self.destroy()


class TraskerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trasker")
        self.geometry("1800x900")

        # Load theme from config (shared with SettingView)
        self.config_file = "settings.ini"
        self.mode = self.load_config()
        if self.mode == "dark":
            self.set_dark_mode()
        else:
            self.set_light_mode()

        # Load an icon.
        icon = tk.PhotoImage(file="assets/favicon.png")
        self.iconphoto(False, icon)

        # Instantiate the core application logic.
        self.trasker = Trasker()

        # Show login dialog.
        login_dialog = LoginDialog(self, self.trasker)
        self.wait_window(login_dialog)
        if login_dialog.result is None:
            self.destroy()
            return
        else:
            self.current_user = login_dialog.result
            self.trasker.set_current_user(self.current_user)

        # Create navigation bar.
        nav_menu = ttk.Frame(self, relief="raised")
        nav_menu.pack(side="top", fill="x")

        # Update the settings button to show the settings view.
        settings_button = ttk.Button(nav_menu, text="Settings",
                                     command=lambda: self.show_frame("SettingView"))
        settings_button.pack(side="right", padx=5, pady=5)

        # Navigation buttons.
        nav_buttons = [
            ("Dashboard", "HomeView"),
            ("Boards", "BoardView"),
            ("All Tasks", "TaskView"),
            ("Epics", "EpicView"),
            ("Sprints", "SprintView"),
            ("Bugs", "BugView"),
            ("Notes", "NotesView"),
            ("Documents", "DocumentsView"),
        ]
        for (text, view_name) in nav_buttons:
            btn = ttk.Button(nav_menu, text=text, command=lambda vn=view_name: self.show_frame(vn))
            btn.pack(side="left", padx=5, pady=5)

        # Container for all views.
        self.frames = {}
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        view_classes = (
        HomeView, EpicView, SprintView, BoardView, TaskView, BugView, NotesView, DocumentsView, SettingView, AdminView)
        for ViewClass in view_classes:
            frame = ViewClass(container, self)
            self.frames[ViewClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomeView")

    def show_frame(self, view_name):
        frame = self.frames.get(view_name)
        if frame:
            frame.tkraise()
            if view_name == "TaskView" and hasattr(frame, "filter_tasks"):
                frame.filter_tasks()
            if view_name == "BoardView" and hasattr(frame, "refresh_board"):
                frame.refresh_board()
            if view_name == "HomeView" and hasattr(frame, "refresh_home"):
                frame.refresh_home()
        else:
            print(f"View {view_name} not found")

    def set_dark_mode(self):
        """Apply dark mode to the root window."""
        bg_color = "#2e2e2e"
        fg_color = "white"
        self.configure(background=bg_color)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TButton", background=bg_color, foreground=fg_color)
        # Additional style configuration for dark mode as needed.

    def set_light_mode(self):
        """Apply light mode to the root window."""
        bg_color = "white"
        fg_color = "black"
        self.configure(background=bg_color)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TButton", background=bg_color, foreground=fg_color)
        # Additional style configuration for light mode as needed.

    def load_config(self):
        """Load the theme from the config file."""
        config = configparser.ConfigParser()
        if os.path.isfile(self.config_file):
            config.read(self.config_file)
            if "Settings" in config and "theme" in config["Settings"]:
                return config["Settings"]["theme"]
        return "light"


if __name__ == "__main__":
    app = TraskerGUI()
    app.mainloop()
