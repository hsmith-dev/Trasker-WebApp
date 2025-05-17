import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from trasker_psql import Trasker

class AdminView(ttk.Frame):
    def __init__(self, parent, controller):
        """
        :param parent: Parent container.
        :param controller: Main application controller (for frame switching).
        """
        super().__init__(parent)
        self.controller = controller
        self.trasker = Trasker()  # Use the Trasker instance for all DB interactions.

        # Create Notebook with two tabs: one for user and one for team management.
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.user_tab = ttk.Frame(self.notebook)
        self.team_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.user_tab, text="User Management")
        self.notebook.add(self.team_tab, text="Team Management")

        self.build_user_tab()
        self.build_team_tab()

        # Back button to return to settings.
        back_button = ttk.Button(self, text="Back to Settings",
                                 command=lambda: controller.show_frame("SettingView"))
        back_button.pack(pady=10)

    # ------------------ USER MANAGEMENT TAB ------------------
    def build_user_tab(self):
        self.user_tree = ttk.Treeview(self.user_tab, columns=("id", "username", "full_name", "email"), show="headings")
        for col in ("id", "username", "full_name", "email"):
            self.user_tree.heading(col, text=col.capitalize())
        self.user_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.user_tab)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add User", command=self.add_user).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Edit User", command=self.edit_user).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Assign to Team", command=self.assign_user_to_team).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Remove from Team", command=self.remove_user_from_team).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_users).grid(row=0, column=4, padx=5)
        ttk.Button(btn_frame, text="Delete User", command=self.delete_user).grid(row=0, column=5, padx=5)

        self.refresh_users()

    def refresh_users(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        try:
            users = self.trasker.get_all_users()
            if users:
                for user in users:
                    self.user_tree.insert("", "end", values=user)
            else:
                messagebox.showinfo("Info", "No users found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_user(self):
        username = simpledialog.askstring("Add User", "Enter username:")
        password = simpledialog.askstring("Add User", "Enter password:", show="*")
        full_name = simpledialog.askstring("Add User", "Enter full name:")
        email = simpledialog.askstring("Add User", "Enter email:")
        if username and password:
            try:
                self.trasker.add_user(username, password, full_name, email)
                messagebox.showinfo("Success", "User added successfully.")
                self.refresh_users()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Input Error", "Username and password are required.")

    def edit_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Edit User", "Please select a user to edit.")
            return
        user = self.user_tree.item(selected[0])['values']
        user_id = user[0]
        new_username = simpledialog.askstring("Edit User", "Enter new username:", initialvalue=user[1])
        new_full_name = simpledialog.askstring("Edit User", "Enter new full name:", initialvalue=user[2])
        new_email = simpledialog.askstring("Edit User", "Enter new email:", initialvalue=user[3])
        if new_username:
            try:
                self.trasker.edit_user(user_id, new_username, new_full_name, new_email)
                messagebox.showinfo("Success", "User updated successfully.")
                self.refresh_users()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def assign_user_to_team(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Assign User", "Please select a user first.")
            return
        user = self.user_tree.item(selected[0])['values']
        user_id = user[0]
        team_id = simpledialog.askinteger("Assign to Team", "Enter team ID to assign the user to:")
        if team_id:
            try:
                self.trasker.assign_user_to_team(user_id, team_id)
                messagebox.showinfo("Success", "User assigned to team successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def remove_user_from_team(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Remove User", "Please select a user first.")
            return
        user = self.user_tree.item(selected[0])['values']
        user_id = user[0]
        team_id = simpledialog.askinteger("Remove from Team", "Enter team ID to remove the user from:")
        if team_id:
            try:
                self.trasker.remove_user_from_team(user_id, team_id)
                messagebox.showinfo("Success", "User removed from team successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Delete User", "Please select a user to delete.")
            return
        user = self.user_tree.item(selected[0])['values']
        user_id = user[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{user[1]}'?")
        if confirm:
            try:
                query = "DELETE FROM users WHERE id = %s"
                self.trasker.db_execute(query, (user_id,))
                messagebox.showinfo("Success", "User deleted successfully.")
                self.refresh_users()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ------------------ TEAM MANAGEMENT TAB ------------------
    def build_team_tab(self):
        self.team_tree = ttk.Treeview(self.team_tab, columns=("id", "name", "description"), show="headings")
        for col in ("id", "name", "description"):
            self.team_tree.heading(col, text=col.capitalize())
        self.team_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.team_tab)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add Team", command=self.add_team).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Edit Team", command=self.edit_team).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Add User to Team", command=self.add_user_to_team).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Remove User from Team", command=self.remove_user_from_team_team).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_teams).grid(row=0, column=4, padx=5)
        ttk.Button(btn_frame, text="Delete Team", command=self.delete_team).grid(row=0, column=5, padx=5)

        self.refresh_teams()

    def refresh_teams(self):
        for item in self.team_tree.get_children():
            self.team_tree.delete(item)
        try:
            teams = self.trasker.get_all_teams()
            if teams:
                for team in teams:
                    self.team_tree.insert("", "end", values=team)
            else:
                messagebox.showinfo("Info", "No teams found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_team(self):
        name = simpledialog.askstring("Add Team", "Enter team name:")
        description = simpledialog.askstring("Add Team", "Enter team description:")
        if name:
            try:
                self.trasker.add_team(name, description)
                messagebox.showinfo("Success", "Team added successfully.")
                self.refresh_teams()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Input Error", "Team name is required.")

    def edit_team(self):
        selected = self.team_tree.selection()
        if not selected:
            messagebox.showwarning("Edit Team", "Please select a team to edit.")
            return
        team = self.team_tree.item(selected[0])['values']
        team_id = team[0]
        new_name = simpledialog.askstring("Edit Team", "Enter new team name:", initialvalue=team[1])
        new_description = simpledialog.askstring("Edit Team", "Enter new team description:", initialvalue=team[2])
        if new_name:
            try:
                self.trasker.edit_team(team_id, new_name, new_description)
                messagebox.showinfo("Success", "Team updated successfully.")
                self.refresh_teams()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def add_user_to_team(self):
        selected = self.team_tree.selection()
        if not selected:
            messagebox.showwarning("Assign User", "Please select a team first.")
            return
        team = self.team_tree.item(selected[0])['values']
        team_id = team[0]
        user_id = simpledialog.askinteger("Add User to Team", "Enter user ID to add to the team:")
        if user_id:
            try:
                self.trasker.assign_user_to_team(user_id, team_id)
                messagebox.showinfo("Success", "User added to team successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def remove_user_from_team_team(self):
        selected = self.team_tree.selection()
        if not selected:
            messagebox.showwarning("Remove User", "Please select a team first.")
            return
        team = self.team_tree.item(selected[0])['values']
        team_id = team[0]
        user_id = simpledialog.askinteger("Remove User from Team", "Enter user ID to remove from the team:")
        if user_id:
            try:
                self.trasker.remove_user_from_team(user_id, team_id)
                messagebox.showinfo("Success", "User removed from team successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_team(self):
        selected = self.team_tree.selection()
        if not selected:
            messagebox.showwarning("Delete Team", "Please select a team to delete.")
            return
        team = self.team_tree.item(selected[0])['values']
        team_id = team[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete team '{team[1]}'?")
        if confirm:
            try:
                query = "DELETE FROM teams WHERE id = %s"
                self.trasker.db_execute(query, (team_id,))
                messagebox.showinfo("Success", "Team deleted successfully.")
                self.refresh_teams()
            except Exception as e:
                messagebox.showerror("Error", str(e))
