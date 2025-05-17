import os
import psycopg2
from colorama import Fore, Style
from psycopg2 import OperationalError, pool


def create_connection_pool(minconn=1, maxconn=10):
    # Define your connection parameters.
    LOCAL_DB_HOST = "192.168.68.123"
    EXTERNAL_DB_HOST = os.environ.get("DB_HOST", "EXTERNAL_IP_ADDRESS")
    DB_NAME = os.environ.get("DB_NAME", "trasker_db")
    DB_USER = os.environ.get("DB_USER", "trasker_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "wotgyx-Risky5-hazsej")
    DB_PORT = os.environ.get("DB_PORT", "5432")

    # Attempt local connection first, fallback to external.
    try:
        pool = psycopg2.pool.SimpleConnectionPool(
            minconn,
            maxconn,
            host=LOCAL_DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            connect_timeout=5
        )
        print("Connected to local database at", LOCAL_DB_HOST)
        return pool
    except Exception as local_error:
        print("Local connection failed:", local_error)
        print("Falling back to external connection...")

    pool = psycopg2.pool.SimpleConnectionPool(
        minconn,
        maxconn,
        host=EXTERNAL_DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        connect_timeout=5
    )
    print("Connected to external database at", EXTERNAL_DB_HOST)
    return pool

def connect():
    """
    Try connecting to the local PostgreSQL server first (using a 5-second timeout).
    If that fails, fall back to the external host.
    """
    # Define the two host options.
    LOCAL_DB_HOST = "192.168.68.123"
    EXTERNAL_DB_HOST = os.environ.get("DB_HOST", "EXTERNAL_IP_ADDRESS")

    # Other connection parameters.
    DB_NAME = os.environ.get("DB_NAME", "trasker_db")
    DB_USER = os.environ.get("DB_USER", "trasker_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "wotgyx-Risky5-hazsej")
    DB_PORT = os.environ.get("DB_PORT", "5432")

    # Try connecting to the local database first.
    try:
        conn = psycopg2.connect(
            host=LOCAL_DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            connect_timeout=5  # Timeout in seconds
        )
        print("Connected to local database at", LOCAL_DB_HOST)
        return conn
    except OperationalError as local_error:
        print("Local connection failed:", local_error)
        print("Falling back to external connection...")

    # Try connecting to the external database.
    try:
        conn = psycopg2.connect(
            host=EXTERNAL_DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            connect_timeout=5  # You can adjust this timeout as needed
        )
        print("Connected to external database at", EXTERNAL_DB_HOST)
        return conn
    except OperationalError as external_error:
        print("External connection failed:", external_error)
        raise external_error


class Trasker:
    def __init__(self):
        self.conn = connect()  # Open connection once
        self.current_user = None
        self.current_team = None

    def db_execute(self, query, params=(), fetch=False, fetch_one=False):
        query = query.strip()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch:
                    result = cursor.fetchall()
                else:
                    result = None
                self.conn.commit()
                return result
        except Exception as e:
            # Optionally handle reconnection logic here if needed.
            self.conn.rollback()
            raise e

    def close(self):
        if self.conn:
            self.conn.close()

    # ---------------- TEAM MANAGEMENT ----------------

    def get_team_name(self, team_id):
        """Returns the team name for the given team_id."""
        query = "SELECT name FROM teams WHERE id = %s"
        result = self.db_execute(query, (team_id,), fetch_one=True)
        return result[0] if result else "Unknown"

    # ---------------- USER MANAGEMENT ----------------

    def verify_user(self, username, password):
        """
        Verify user credentials.
        Returns a tuple (id, username, full_name, email) if valid, or None otherwise.
        """
        query = "SELECT id, username, full_name, email FROM users WHERE username = %s AND password = %s"
        user = self.db_execute(query, (username, password), fetch_one=True)
        return user

    def set_current_user(self, user):
        """
        Set the current user.
        Also, set the active team to the first team associated with the user.
        """
        self.current_user = user
        query = "SELECT team_id FROM user_team WHERE user_id = %s LIMIT 1"
        result = self.db_execute(query, (user[0],), fetch_one=True)
        if result:
            self.current_team = result[0]
        else:
            self.current_team = None

    def set_current_team(self, team_id):
        """Set the current active team."""
        self.current_team = team_id

    def get_username(self, user_id):
        """Given a user ID, return the username."""
        query = "SELECT username FROM users WHERE id = %s LIMIT 1"
        result = self.db_execute(query, (user_id,), fetch_one=True)
        return result[0] if result else "Unknown"

    def get_user_id_from_username(self, username):
        """Given a username, return the user ID."""
        query = "SELECT id FROM users WHERE username = %s LIMIT 1"
        result = self.db_execute(query, (username,), fetch_one=True)
        return result[0] if result else "Unknown"

    def get_user_teams(self, user_id):
        """Retrieve all team IDs associated with the given user."""
        query = "SELECT team_id FROM user_team WHERE user_id = %s"
        result = self.db_execute(query, (user_id,), fetch=True)
        return [row[0] for row in result] if result else []

    # ---------------- TASK MANAGEMENT ----------------

    def add_task(self, title, description, due_date, status="Pending", category="General",
                 priority="Medium", recurrence="None", parent_task_id=None, sprint_id=None,
                 user_id=None, team_id=None):
        """
        Add a task. If user_id or team_id are not provided, assign the task to the current user and active team.
        """
        if user_id is None and self.current_user:
            user_id = self.current_user[0]
        if team_id is None:
            team_id = self.current_team
        query = """
            INSERT INTO tasks 
              (title, description, due_date, status, category, priority, recurrence, parent_task_id, sprint_id, user_id, team_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.db_execute(query, (title, description, due_date, status, category, priority,
                                  recurrence, parent_task_id, sprint_id, user_id, team_id))

    def delete_task(self, task_id):
        query = "DELETE FROM tasks WHERE id = %s"
        self.db_execute(query, (task_id,))

    def task_mark_completed(self, task_id):
        query = "UPDATE tasks SET status = 'Completed' WHERE id = %s"
        self.db_execute(query, (task_id,))

    def task_mark_archived(self, task_id):
        query = "UPDATE tasks SET status = 'Archived' WHERE id = %s"
        self.db_execute(query, (task_id,))

    def task_change_status(self, task_id, status):
        query = "UPDATE tasks SET status = %s WHERE id = %s"
        self.db_execute(query, (status, task_id))

    def task_change_title(self, task_id, title):
        query = "UPDATE tasks SET title = %s WHERE id = %s"
        self.db_execute(query, (title, task_id))

    def task_change_description(self, task_id, description):
        query = "UPDATE tasks SET description = %s WHERE id = %s"
        self.db_execute(query, (description, task_id))

    def task_change_priority(self, task_id, priority):
        query = "UPDATE tasks SET priority = %s WHERE id = %s"
        self.db_execute(query, (priority, task_id))

    def task_change_category(self, task_id, category):
        query = "UPDATE tasks SET category = %s WHERE id = %s"
        self.db_execute(query, (category, task_id))

    # ---------------- TASK SESSION TRACKING ----------------

    def start_task_timer(self, task_id):
        query = "INSERT INTO task_sessions (task_id, start_time) VALUES (%s, CURRENT_TIMESTAMP)"
        self.db_execute(query, (task_id,))

    def stop_task_timer(self, task_id):
        query = "SELECT id, start_time FROM task_sessions WHERE task_id = %s AND end_time IS NULL"
        session = self.db_execute(query, (task_id,), fetch_one=True)
        if session:
            session_id, start_time = session
            update_query = """
                UPDATE task_sessions 
                SET end_time = CURRENT_TIMESTAMP, 
                    elapsed_time = EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) - EXTRACT(EPOCH FROM start_time::timestamp)
                WHERE id = %s
            """
            self.db_execute(update_query, (session_id,))

    def get_total_task_time(self, task_id):
        query = "SELECT SUM(elapsed_time) FROM task_sessions WHERE task_id = %s"
        result = self.db_execute(query, (task_id,), fetch_one=True)
        return result[0] if result and result[0] is not None else 0

    def is_timer_running(self, task_id):
        query = "SELECT id FROM task_sessions WHERE task_id = %s AND end_time IS NULL"
        session = self.db_execute(query, (task_id,), fetch_one=True)
        return session is not None

    def list_all_tasks(self):
        """
        List all tasks visible to the current user: tasks owned by the user or shared in the active team.
        """
        query = """
            SELECT t.id, t.title, t.description, t.due_date, t.status, t.category, t.priority, t.recurrence,
                   t.parent_task_id, t.sprint_id,
                   u.username,
                   tm.name as team_name
            FROM tasks t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN teams tm ON t.team_id = tm.id
            WHERE t.user_id = %s OR t.team_id = %s
        """
        return self.db_execute(query, (self.current_user[0], self.current_team), fetch=True)

    def list_tasks(self):
        """
        List active tasks (not completed) visible to the current user.
        """
        query = """
            SELECT t.id, t.title, t.description, t.due_date, t.status, t.category, t.priority, t.recurrence,
                   t.parent_task_id, t.sprint_id,
                   u.username,
                   tm.name as team_name
            FROM tasks t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN teams tm ON t.team_id = tm.id
            WHERE (t.user_id = %s OR t.team_id = %s) AND t.status != 'Completed'
            ORDER BY t.due_date ASC,
                CASE t.priority 
                    WHEN 'Critical' THEN 1 
                    WHEN 'High' THEN 2 
                    WHEN 'Medium' THEN 3 
                    WHEN 'Low' THEN 4 
                END ASC
        """
        tasks = self.db_execute(query, (self.current_user[0], self.current_team), fetch=True)
        if not tasks:
            print(Fore.RED + "[DEBUG] No tasks found in the database." + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"[DEBUG] Found {len(tasks)} tasks in the database." + Style.RESET_ALL)
        return tasks

    def search_task_by_keyword(self, keyword):
        query = """
            SELECT t.id, t.title, t.description, t.due_date, t.status, t.category, t.priority, t.recurrence,
                   t.parent_task_id, t.sprint_id,
                   u.username,
                   tm.name as team_name
            FROM tasks t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN teams tm ON t.team_id = tm.id
            WHERE (t.user_id = %s OR t.team_id = %s) AND (t.title ILIKE %s OR t.description ILIKE %s)
        """
        return self.db_execute(query, (self.current_user[0], self.current_team, f"%{keyword}%", f"%{keyword}%"), fetch=True)

    def list_tasks_by_epic(self, epic_id):
        query = """
            SELECT t.id, t.title, t.description, t.due_date, t.status, t.category, t.priority, t.recurrence,
                   t.parent_task_id, t.sprint_id,
                   u.username,
                   tm.name as team_name
            FROM tasks t
            JOIN sprints s ON t.sprint_id = s.id
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN teams tm ON t.team_id = tm.id
            WHERE s.epic_id = %s AND (t.user_id = %s OR t.team_id = %s)
        """
        return self.db_execute(query, (epic_id, self.current_user[0], self.current_team), fetch=True)

    def list_sprint_tasks(self, sprint_id):
        query = """
            SELECT t.id, t.title, t.description, t.due_date, t.status, t.category, t.priority, t.recurrence,
                   t.parent_task_id, t.sprint_id,
                   u.username,
                   tm.name as team_name
            FROM tasks t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN teams tm ON t.team_id = tm.id
            WHERE t.sprint_id = %s AND (t.user_id = %s OR t.team_id = %s)
        """
        return self.db_execute(query, (sprint_id, self.current_user[0], self.current_team), fetch=True)

    def list_task_by_id(self, task_id):
        query = """
            SELECT t.id, t.title, t.description, t.due_date, t.status, t.category, t.priority, t.recurrence,
                   t.parent_task_id, t.sprint_id,
                   u.username,
                   tm.name as team_name
            FROM tasks t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN teams tm ON t.team_id = tm.id
            WHERE t.id = %s AND (t.user_id = %s OR t.team_id = %s)
        """
        tasks = self.db_execute(query, (task_id, self.current_user[0], self.current_team), fetch=True)
        if not tasks:
            return None
        return tasks[0]

    # ---------------- BUGS MANAGEMENT ----------------

    def add_bug(self, title, description, status, created_date, resolved_date, task_id,
                user_id=None, team_id=None):
        """
        Add a bug.
        If user_id or team_id are not provided, assign the bug to the current user and active team.
        Parameters:
          - title: A string bug title.
          - description: A string bug description.
          - status: A string status (e.g. "Open").
          - created_date: A string date (e.g. "2025-02-09").
          - resolved_date: A string date or None.
          - task_id: The id of the related task (can be None).
          - user_id: Optional; if not provided, the bug is assigned to the current user.
          - team_id: Optional; if not provided, the bug is assigned to the current team.
        """
        # If user_id or team_id are not given, use the current user/team.
        if user_id is None and self.current_user:
            user_id = self.current_user[0]
        if team_id is None:
            team_id = self.current_team

        query = """
            INSERT INTO bugs 
              (title, description, status, created_date, resolved_date, task_id, user_id, team_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.db_execute(query, (title, description, status, created_date, resolved_date, task_id, user_id, team_id))

    def list_all_bugs(self):
        query = """
            SELECT b.id, b.title, b.description, b.status, b.created_date, b.resolved_date, b.task_id,
                   u.username,
                   tm.name as team_name
            FROM bugs b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN teams tm ON b.team_id = tm.id
            WHERE b.user_id = %s OR b.team_id = %s
        """
        return self.db_execute(query, (self.current_user[0], self.current_team), fetch=True)

    def list_bugs_by_task(self, task_id):
        query = "SELECT * FROM bugs WHERE task_id = %s AND (user_id = %s OR team_id = %s)"
        return self.db_execute(query, (task_id, self.current_user[0], self.current_team), fetch=True)

    def get_bug(self, bug_id):
        """
        Retrieve a single bug by its id.
        Returns a tuple:
        (id, title, description, status, created_date, resolved_date, task_id, username, team_name)
        """
        query = """
            SELECT b.id, b.title, b.description, b.status, b.created_date, b.resolved_date, b.task_id,
                   u.username,
                   tm.name as team_name
            FROM bugs b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN teams tm ON b.team_id = tm.id
            WHERE b.id = %s
        """
        return self.db_execute(query, (bug_id,), fetch_one=True)

    def edit_bug(self, bug_id, title, description, status, created_date, resolved_date, task_id):
        """Updates the bug with the provided values."""
        #TODO Figure out code to support when task_id is none, currently must be some id
        query = """
            UPDATE bugs
            SET title = %s,
                description = %s,
                status = %s,
                created_date = %s,
                resolved_date = %s,
                task_id = %s
            WHERE id = %s
        """
        return self.db_execute(query, (title, description, status, created_date, resolved_date, task_id, bug_id))

    def delete_bug(self, bug_id):
        """Deletes the bug with the provided id."""
        query = """DELETE FROM bugs WHERE id = %s"""
        return self.db_execute(query, (bug_id,))
    # ---------------- NOTES MANAGEMENT ----------------

    def add_note(self, note, note_type=None, reference_id=None):
        if self.current_user:
            user_id = self.current_user[0] if isinstance(self.current_user, (tuple, list)) else self.current_user
        else:
            user_id = None
        if self.current_team:
            team_id = self.current_team[0] if isinstance(self.current_team, (tuple, list)) else self.current_team
        else:
            team_id = None
        query = "INSERT INTO notes (note, note_type, reference_id, user_id, team_id) VALUES (%s, %s, %s, %s, %s)"
        self.db_execute(query, (note, note_type, reference_id, user_id, team_id))

    def list_notes(self, note_type=None, reference_id=None):
        if note_type and reference_id:
            query = "SELECT * FROM notes WHERE note_type = %s AND reference_id = %s AND (user_id = %s OR team_id = %s)"
            return self.db_execute(query, (note_type, reference_id, self.current_user[0], self.current_team),
                                   fetch=True)
        elif note_type:
            query = "SELECT * FROM notes WHERE note_type = %s AND (user_id = %s OR team_id = %s)"
            return self.db_execute(query, (note_type, self.current_user[0], self.current_team), fetch=True)
        elif reference_id:
            query = "SELECT * FROM notes WHERE reference_id = %s AND (user_id = %s OR team_id = %s)"
            return self.db_execute(query, (reference_id, self.current_user[0], self.current_team), fetch=True)
        else:
            query = "SELECT * FROM notes WHERE (user_id = %s OR team_id = %s)"
            return self.db_execute(query, (self.current_user[0], self.current_team), fetch=True)

    def update_note(self, note_id, note):
        query = "UPDATE notes SET note = %s, updated_date = CURRENT_TIMESTAMP WHERE id = %s"
        self.db_execute(query, (note, note_id))

    def delete_note(self, note_id):
        query = "DELETE FROM notes WHERE id = %s"
        self.db_execute(query, (note_id))

    def get_note(self, note_id):
        print(note_id)
        query = "SELECT * FROM notes WHERE id = %s"
        result = self.db_execute(query, (note_id), fetch_one=True)
        print(query)
        print(result)
        return result

    # ---------------- DOCUMENTS MANAGEMENT ----------------

    def add_document(self, note_id, filename, mimetype, document_blob):
        user_id = self.current_user[0] if self.current_user else None
        team_id = self.current_team
        query = "INSERT INTO documents (note_id, filename, mimetype, document_blob, user_id, team_id) VALUES (%s, %s, %s, %s, %s, %s)"
        self.db_execute(query, (note_id, filename, mimetype, document_blob, user_id, team_id))

    def delete_document(self, document_id):
        query = "DELETE FROM documents WHERE id = %s"
        self.db_execute(query, (document_id,))

    def list_all_documents(self):
        query = """
            SELECT d.id, d.note_id, d.filename, d.mimetype, d.upload_date,
                   u.username,
                   tm.name as team_name
            FROM documents d
            LEFT JOIN users u ON d.user_id = u.id
            LEFT JOIN teams tm ON d.team_id = tm.id
            WHERE d.user_id = %s OR d.team_id = %s
        """
        return self.db_execute(query, (self.current_user[0], self.current_team), fetch=True)

    def get_document(self, document_id):
        query = """
            SELECT d.id, d.note_id, d.filename, d.mimetype, d.document_blob, d.upload_date,
                   u.username,
                   tm.name as team_name
            FROM documents d
            LEFT JOIN users u ON d.user_id = u.id
            LEFT JOIN teams tm ON d.team_id = tm.id
            WHERE d.id = %s AND (d.user_id = %s OR d.team_id = %s)
        """
        return self.db_execute(query, (document_id, self.current_user[0], self.current_team), fetch_one=True)

    def update_document(self, document_id, new_blob):
        query = "UPDATE documents SET document_blob = %s, upload_date = CURRENT_TIMESTAMP WHERE id = %s"
        self.db_execute(query, (new_blob, document_id))

    # ---------------- SPRINT MANAGEMENT ----------------

    def create_epic(self, name, description, start_date, end_date, user_id, team_id):
        query = """
            INSERT INTO epics (name, description, start_date, end_date, user_id, team_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.db_execute(query, (name, description, start_date, end_date, user_id, team_id))

    def list_epics(self):
        query = """
            SELECT e.id, e.name, e.description, e.start_date, e.end_date, u.username, tm.name as team_name 
            FROM epics e 
            LEFT JOIN users u ON e.user_id = u.id 
            LEFT JOIN teams tm ON e.team_id = tm.id
            WHERE e.user_id = %s OR e.team_id = %s
        """
        return self.db_execute(query, (self.current_user[0], self.current_team), fetch=True)

    def list_epic_by_id(self, epic_id):
        query = "SELECT * FROM epics WHERE id = %s"
        return self.db_execute(query, (epic_id,), fetch_one=True)

    def delete_epic(self, epic_id):
        query = "DELETE FROM epics WHERE id = %s"
        return self.db_execute(query, (epic_id,))

    def list_epic_sprints(self, epic_id):
        query = """
            SELECT s.id, s.title, s.description, s.start_date, s.end_date, s.epic_id, u.username, tm.name as team_name 
            FROM sprints s 
            LEFT JOIN users u ON s.user_id = u.id 
            LEFT JOIN teams tm ON s.team_id = tm.id
            WHERE s.epic_id = %s AND (s.user_id = %s OR s.team_id = %s)
        """
        return self.db_execute(query, (epic_id, self.current_user[0], self.current_team), fetch=True)

    def create_sprint(self, title, description, start_date, end_date, epic_id=None):
        user_id = self.current_user[0] if self.current_user else None
        team_id = self.current_team
        query = "INSERT INTO sprints (title, description, start_date, end_date, epic_id, user_id, team_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.db_execute(query, (title, description, start_date, end_date, epic_id, user_id, team_id))

    def list_sprints(self):
        query = """
            SELECT s.id, s.title, s.description, s.start_date, s.end_date, s.epic_id, u.username, tm.name as team_name 
            FROM sprints s 
            LEFT JOIN users u ON s.user_id = u.id 
            LEFT JOIN teams tm ON s.team_id = tm.id
            WHERE s.user_id = %s OR s.team_id = %s
        """
        return self.db_execute(query, (self.current_user[0], self.current_team), fetch=True)

    def list_sprint_tasks(self, sprint_id):
        query = """
            SELECT t.id, t.title, t.description, t.due_date, t.status, t.category, t.priority, t.recurrence,
                   t.parent_task_id, t.sprint_id,
                   u.username,
                   tm.name as team_name
            FROM tasks t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN teams tm ON t.team_id = tm.id
            WHERE t.sprint_id = %s AND (t.user_id = %s OR t.team_id = %s)
        """
        return self.db_execute(query, (sprint_id, self.current_user[0], self.current_team), fetch=True)

    def list_sprint_by_id(self, sprint_id):
        query = "SELECT * FROM sprints WHERE id = %s"
        return self.db_execute(query, (sprint_id), fetch=True)

    # ---------------- TASK QUERIES ----------------

    def list_task_by_id(self, task_id):
        query = """
            SELECT t.id, t.title, t.description, t.due_date, t.status, t.category, t.priority, t.recurrence,
                   t.parent_task_id, t.sprint_id,
                   u.username,
                   tm.name as team_name
            FROM tasks t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN teams tm ON t.team_id = tm.id
            WHERE t.id = %s AND (t.user_id = %s OR t.team_id = %s)
        """
        tasks = self.db_execute(query, (task_id, self.current_user[0], self.current_team), fetch=True)
        if not tasks:
            return None
        return tasks[0]

    def print_tasks(self, tasks):
        if not tasks:
            print(Fore.CYAN + "No active tasks found." + Style.RESET_ALL)
            return
        for task in tasks:
            print(f"{Fore.BLUE}Task {task[0]}{Style.RESET_ALL}: {task[1]}")
            print(f"    {Fore.LIGHTBLUE_EX}Due: {Style.RESET_ALL}{task[3]} | {Fore.LIGHTBLUE_EX}Status: {Style.RESET_ALL}{task[4]}")
            print(f"    {Fore.LIGHTBLUE_EX}Category: {Style.RESET_ALL}{task[5]} | {Fore.LIGHTBLUE_EX}Priority: {Style.RESET_ALL}{task[6]}")

    def search_task_by_keyword(self, keyword):
        query = """
            SELECT t.id, t.title, t.description, t.due_date, t.status, t.category, t.priority, t.recurrence,
                   t.parent_task_id, t.sprint_id,
                   u.username,
                   tm.name as team_name
            FROM tasks t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN teams tm ON t.team_id = tm.id
            WHERE (t.user_id = %s OR t.team_id = %s) AND (t.title ILIKE %s OR t.description ILIKE %s)
        """
        return self.db_execute(query, (self.current_user[0], self.current_team, f"%{keyword}%", f"%{keyword}%"), fetch=True)

    def list_all_bugs(self):
        query = """
            SELECT b.id, b.title, b.description, b.status, b.created_date, b.resolved_date, b.task_id,
                   u.username,
                   tm.name as team_name
            FROM bugs b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN teams tm ON b.team_id = tm.id
            WHERE b.user_id = %s OR b.team_id = %s
        """
        return self.db_execute(query, (self.current_user[0], self.current_team), fetch=True)

    # ----------------- USER OPERATIONS -----------------

    def get_all_users(self):
        query = "SELECT id, username, full_name, email FROM users"
        return self.db_execute(query, fetch=True)

    def add_user(self, username, password, full_name, email):
        query = "INSERT INTO users (username, password, full_name, email) VALUES (%s, %s, %s, %s)"
        self.db_execute(query, (username, password, full_name, email))

    def edit_user(self, user_id, new_username, new_full_name, new_email):
        query = "UPDATE users SET username = %s, full_name = %s, email = %s WHERE id = %s"
        self.db_execute(query, (new_username, new_full_name, new_email, user_id))

    def assign_user_to_team(self, user_id, team_id):
        query = "INSERT INTO user_team (user_id, team_id) VALUES (%s, %s)"
        self.db_execute(query, (user_id, team_id))

    def remove_user_from_team(self, user_id, team_id):
        query = "DELETE FROM user_team WHERE user_id = %s AND team_id = %s"
        self.db_execute(query, (user_id, team_id))

    # ----------------- TEAM OPERATIONS -----------------

    def get_all_teams(self):
        query = "SELECT id, name, description FROM teams"
        return self.db_execute(query, fetch=True)

    def add_team(self, name, description):
        query = "INSERT INTO teams (name, description) VALUES (%s, %s)"
        self.db_execute(query, (name, description))

    def edit_team(self, team_id, new_name, new_description):
        query = "UPDATE teams SET name = %s, description = %s WHERE id = %s"
        self.db_execute(query, (new_name, new_description, team_id))


# End of Trasker class
