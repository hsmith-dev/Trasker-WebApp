import configparser
import os
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

class SettingView(tk.Frame):
    def __init__(self, parent, controller, version="dev_2025-02-10"):
        super().__init__(parent)
        self.controller = controller
        self.version = version
        self.config_file = "settings.ini"

        # Load the current mode from config.
        self.mode = self.load_config()  # "light" or "dark"

        # (Optional) Update the view's appearance.
        if self.mode == "dark":
            self.set_dark_mode()
        else:
            self.set_light_mode()

        # Title for the settings view.
        title_label = ttk.Label(self, text="Settings", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Toggle theme button.
        toggle_theme_button = ttk.Button(self, text="Toggle Theme", command=self.toggle_mode)
        toggle_theme_button.pack(pady=5)

        # Section for showing app details.
        details_frame = ttk.Frame(self, borderwidth=1, relief="groove", padding=10)
        details_frame.pack(fill=tk.X, padx=10, pady=10)

        details_title = ttk.Label(details_frame, text="App Details", font=("Arial", 14, "bold"))
        details_title.pack(anchor=tk.W)

        version_label = ttk.Label(details_frame, text=f"Version: {self.version}", font=("Arial", 12))
        version_label.pack(anchor=tk.W, pady=2)

        additional_label = ttk.Label(details_frame, text="Additional functionality coming soon...",
                                     font=("Arial", 10, "italic"))
        additional_label.pack(anchor=tk.W, pady=2)

        # Add a clickable link to the website.
        website_label = ttk.Label(details_frame, text="Visit Website", font=("Arial", 10, "underline"),
                                  foreground="blue", cursor="hand2")
        website_label.pack(anchor=tk.W, pady=2)
        website_label.bind("<Button-1>", lambda e: webbrowser.open("https://trasker.app"))

        # Only show the Admin Panel button if the current user is allowed.
        # For this initial version, only user with id == 1 should see it.
        # Depending on how you store the current user, you might need to adjust this.
        if hasattr(controller, "current_user"):
            # If current_user is a tuple (e.g. (id, username, ...))
            user_id = controller.current_user[0] if isinstance(controller.current_user, (list, tuple)) else controller.current_user
            if user_id == 1:
                admin_button = ttk.Button(self, text="Admin Panel", command=lambda: self.controller.show_frame("AdminView"))
                admin_button.pack(pady=10)
        else:
            # Alternatively, if there's no current_user attribute, you can disable the button or not show it at all.
            pass

    def toggle_mode(self):
        """Toggle between light and dark modes."""
        if self.mode == "light":
            self.mode = "dark"
            self.set_dark_mode()
        else:
            self.mode = "light"
            self.set_light_mode()
        self.save_config()
        # Update the theme for all views using the controller's frames.
        for frame in self.controller.frames.values():
            if hasattr(frame, "update_theme"):
                frame.update_theme()

    def set_dark_mode(self):
        """Configure dark mode."""
        bg_color = "#2e2e2e"
        fg_color = "white"
        accent_color = "#5c80e7"
        self.configure(background=bg_color)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TButton", background=bg_color, foreground=fg_color)
        style.map("TButton", background=[('active', accent_color)])
        style.configure("Treeview", background=bg_color, foreground=fg_color, fieldbackground=bg_color, rowheight=50)
        style.configure("Treeview.Heading", background=accent_color, foreground=fg_color)
        style.map("Treeview.Heading", foreground=[("active", "black")])

    def set_light_mode(self):
        """Configure light mode."""
        bg_color = "white"
        fg_color = "black"
        accent_color = "#5c80e7"
        self.configure(background=bg_color)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TButton", background=bg_color, foreground=fg_color)
        style.map("TButton", background=[('active', accent_color)])
        style.configure("Treeview", background=bg_color, foreground=fg_color, fieldbackground=bg_color, rowheight=50)
        style.configure("Treeview.Heading", background=accent_color, foreground=bg_color)

    def save_config(self):
        """Save the theme setting to the config file."""
        config = configparser.ConfigParser()
        config["Settings"] = {"theme": self.mode}
        with open(self.config_file, "w") as configfile:
            config.write(configfile)

    def load_config(self):
        """Load the theme setting from the config file."""
        config = configparser.ConfigParser()
        if os.path.isfile(self.config_file):
            config.read(self.config_file)
            if "Settings" in config and "theme" in config["Settings"]:
                return config["Settings"]["theme"]
        return "light"
