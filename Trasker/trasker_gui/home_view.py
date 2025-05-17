import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HomeView(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        mode = self.controller.mode
        if mode == "dark":
            self.bg_color = "#2e2e2e"
            self.fg_color = "white"
            self.chart_text_color = "white"
        else:
            self.bg_color = "white"
            self.fg_color = "black"
            self.chart_text_color = "black"

        super().__init__(parent, bg=self.bg_color)

        # Header
        self.header = ttk.Label(self, text="Dashboard", font=("Arial", 24, "bold"))
        self.header.configure(background=self.bg_color, foreground=self.fg_color)
        self.header.pack(padx=10, pady=20)

        # --- Team Filter Panel ---
        team_filter_frame = ttk.Frame(self, padding=(10, 0))
        team_filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(team_filter_frame, text="Filter by Team:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.team_filter = ttk.Combobox(team_filter_frame, state="readonly", width=20)
        self.team_filter.pack(side=tk.LEFT, padx=5)
        ttk.Button(team_filter_frame, text="Apply Team Filter", command=self.update_charts).pack(side=tk.LEFT, padx=5)
        self.load_team_dropdown()

        # Create a frame to hold the chart cards in a grid.
        self.charts_frame = tk.Frame(self, bg=self.bg_color)
        self.charts_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Create two chart cards.
        self.last_sprint_chart = self.create_chart_card(self.charts_frame, "Last Sprint Completion")
        self.overall_chart = self.create_chart_card(self.charts_frame, "Overall Task Completion")

        # Arrange them in one row (two columns).
        self.last_sprint_chart["frame"].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.overall_chart["frame"].grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.charts_frame.columnconfigure(0, weight=1)
        self.charts_frame.columnconfigure(1, weight=1)
        self.charts_frame.rowconfigure(0, weight=1)

        # Initial chart drawing.
        self.update_charts()

    def load_team_dropdown(self):
        """
        Populate the team filter combobox with teams the current user belongs to.
        Assumes the current user is stored in self.controller.trasker.current_user.
        """
        if hasattr(self.controller.trasker, "current_user") and self.controller.trasker.current_user:
            # Get the current user ID. If current_user is a tuple, extract the first element.
            user_id = self.controller.trasker.current_user
            if isinstance(user_id, tuple):
                user_id = user_id[0]
            query = """
                SELECT t.id, t.name
                FROM teams t
                JOIN user_team ut ON t.id = ut.team_id
                WHERE ut.user_id = %s
            """
            rows = self.controller.trasker.db_execute(query, (user_id,), fetch=True)
            team_options = ["All"] + [row[1] for row in rows]
            self.team_map = {row[1]: row[0] for row in rows}  # Map team name to team id.
            self.team_filter["values"] = team_options
            self.team_filter.current(0)
        else:
            self.team_filter["values"] = ["All"]
            self.team_filter.current(0)
            self.team_map = {}

    def create_chart_card(self, parent, title_text):
        """
        Create a card that displays a title and embeds a matplotlib pie chart.
        Returns a dict with keys: "frame", "canvas", "figure", and "ax".
        """
        card_frame = tk.Frame(parent, relief="raised", padx=10, pady=10, bg=self.bg_color)
        title_label = ttk.Label(card_frame, text=title_text, font=("Arial", 14, "bold"))
        title_label.configure(background=self.bg_color, foreground=self.fg_color)
        title_label.pack(anchor="w")

        figure = Figure(figsize=(3, 3), dpi=100, facecolor=self.bg_color)
        ax = figure.add_subplot(111)
        ax.set_facecolor(self.bg_color)

        canvas = FigureCanvasTkAgg(figure, master=card_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        return {"frame": card_frame, "canvas": canvas, "figure": figure, "ax": ax}

    def update_charts(self):
        """Update both pie charts using the current chart text color and applied team filter."""
        self.update_last_sprint_chart()
        self.update_overall_chart()

    def update_last_sprint_chart(self):
        """Update the last sprint pie chart with optional team filtering."""
        sprints = self.controller.trasker.list_sprints()
        if sprints:
            last_sprint = sprints[-1]
            sprint_id = last_sprint[0]
            tasks = self.controller.trasker.list_sprint_tasks(sprint_id)
        else:
            tasks = self.controller.trasker.list_all_tasks()

        # Apply team filter if set.
        team_filter_value = self.team_filter.get()
        if team_filter_value and team_filter_value != "All":
            team_id = self.team_map.get(team_filter_value)
            if team_id is not None:
                # Assuming team_id is at index 11 in the task tuple.
                tasks = [task for task in tasks if task[11] == team_id]

        total = len(tasks)
        if total == 0:
            completed = 0
            not_completed = 0
        else:
            completed = len([task for task in tasks if task[4].lower() == "completed"])
            not_completed = total - completed

        ax = self.last_sprint_chart["ax"]
        ax.clear()
        if total == 0:
            ax.text(0.5, 0.5, "No Data", horizontalalignment="center", verticalalignment="center",
                    transform=ax.transAxes, fontsize=18, color=self.chart_text_color)
        else:
            labels = ["Completed", "Not Completed"]
            sizes = [completed, not_completed]
            ax.pie(sizes, labels=labels, autopct=lambda pct: f"{pct:.1f}%", startangle=90,
                   textprops={"fontsize": 16, "color": self.chart_text_color})
            ax.axis("equal")
        self.last_sprint_chart["canvas"].draw()

    def update_overall_chart(self):
        """Update the overall task completion pie chart with optional team filtering."""
        tasks = self.controller.trasker.list_all_tasks()

        # Apply team filter if set.
        team_filter_value = self.team_filter.get()
        if team_filter_value and team_filter_value != "All":
            team_id = self.team_map.get(team_filter_value)
            if team_id is not None:
                tasks = [task for task in tasks if task[11] == team_id]

        total = len(tasks)
        if total == 0:
            completed = 0
            not_completed = 0
        else:
            completed = len([task for task in tasks if task[4].lower() == "completed"])
            not_completed = total - completed

        ax = self.overall_chart["ax"]
        ax.clear()
        if total == 0:
            ax.text(0.5, 0.5, "No Data", horizontalalignment="center", verticalalignment="center",
                    transform=ax.transAxes, fontsize=18, color=self.chart_text_color)
        else:
            labels = ["Completed", "Not Completed"]
            sizes = [completed, not_completed]
            ax.pie(sizes, labels=labels, autopct=lambda pct: f"{pct:.1f}%", startangle=90,
                   textprops={"fontsize": 16, "color": self.chart_text_color})
            ax.axis("equal")
        self.overall_chart["canvas"].draw()

    def update_theme(self):
        """Update HomeView's theme based on the controller's mode."""
        mode = self.controller.mode
        if mode == "dark":
            self.bg_color = "#2e2e2e"
            self.fg_color = "white"
            self.chart_text_color = "white"
        else:
            self.bg_color = "white"
            self.fg_color = "black"
            self.chart_text_color = "black"

        self.configure(bg=self.bg_color)
        self.header.configure(background=self.bg_color, foreground=self.fg_color)
        self.charts_frame.configure(bg=self.bg_color)
        self.team_filter.configure(background=self.bg_color, foreground=self.fg_color)
        for chart in [self.last_sprint_chart, self.overall_chart]:
            chart["frame"].configure(bg=self.bg_color)
            chart["frame"].winfo_children()[0].configure(background=self.bg_color, foreground=self.fg_color)
            chart["figure"].set_facecolor(self.bg_color)
            chart["ax"].set_facecolor(self.bg_color)
        self.update_charts()

    def refresh_home(self):
        self.update_charts()
