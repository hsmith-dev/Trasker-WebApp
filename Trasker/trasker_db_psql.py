import psycopg2
from psycopg2 import sql, OperationalError
from datetime import datetime
import os


def connect():
    """
    Try connecting to the local PostgreSQL server first (using a 5-second timeout).
    If that fails, fall back to the external host.
    """
    # Define the two host options.
    LOCAL_DB_HOST = "127.0.0.1"
    # EXTERNAL_DB_HOST = os.environ.get("DB_HOST", "IP_ADDRESS_HERE")

    # Other connection parameters.
    DB_NAME = os.environ.get("DB_NAME", "trasker_db")
    DB_USER = os.environ.get("DB_USER", "trasker_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "wotgyx-Risky5-hazsej")
    DB_PORT = os.environ.get("DB_PORT", "5433")

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
    # try:
    #     conn = psycopg2.connect(
    #         host=EXTERNAL_DB_HOST,
    #         database=DB_NAME,
    #         user=DB_USER,
    #         password=DB_PASSWORD,
    #         port=DB_PORT,
    #         connect_timeout=5  # You can adjust this timeout as needed
    #     )
    #     print("Connected to external database at", EXTERNAL_DB_HOST)
    #     return conn
    # except OperationalError as external_error:
    #     print("External connection failed:", external_error)
    #     raise external_error

def setup():
    """Setup the database with tables for multi-user support:
       - Users, Teams, and a mapping table user_team.
       - Existing tables (epics, sprints, tasks, bugs, notes, documents) now include user_id and team_id.
    """
    conn = connect()
    cursor = conn.cursor()

    # ---- New Tables for Multi-User Support ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            email TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_team (
            user_id INTEGER,
            team_id INTEGER,
            PRIMARY KEY (user_id, team_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
        )
    ''')

    # ---- Existing Tables Updated for Ownership & Team Association ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS epics (
            id SERIAL PRIMARY KEY,
            name TEXT,
            description TEXT,
            start_date TEXT,
            end_date TEXT,
            user_id INTEGER,
            team_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sprints (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            start_date TEXT,
            end_date TEXT,
            epic_id INTEGER DEFAULT NULL,
            user_id INTEGER,
            team_id INTEGER,
            FOREIGN KEY (epic_id) REFERENCES epics(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'Pending',
            category TEXT DEFAULT 'General',
            priority TEXT DEFAULT 'Medium',
            recurrence TEXT DEFAULT 'None',
            parent_task_id INTEGER DEFAULT NULL,
            sprint_id INTEGER DEFAULT NULL,
            user_id INTEGER,
            team_id INTEGER,
            FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE SET NULL,
            FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_sessions (
            id SERIAL PRIMARY KEY,
            task_id INTEGER NOT NULL,
            start_time TEXT,
            end_time TEXT,
            elapsed_time INTEGER DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bugs (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Open',
            created_date TEXT,
            resolved_date TEXT,
            task_id INTEGER DEFAULT NULL,
            user_id INTEGER,
            team_id INTEGER,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            note TEXT NOT NULL,
            note_type TEXT,      -- 'epic', 'sprint', 'task', or 'bug'
            reference_id INTEGER, -- The ID of the associated epic/sprint/task/bug
            user_id INTEGER,
            team_id INTEGER,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            note_id INTEGER,      -- The note this document is attached to.
            filename TEXT,
            mimetype TEXT,
            document_blob BYTEA,
            upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            team_id INTEGER,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print("[SETUP] Database initialized successfully.")

def drop():
    """Drop all tables in the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS documents")
    cursor.execute("DROP TABLE IF EXISTS notes")
    cursor.execute("DROP TABLE IF EXISTS bug_tasks")
    cursor.execute("DROP TABLE IF EXISTS bugs")
    cursor.execute("DROP TABLE IF EXISTS task_sessions")
    cursor.execute("DROP TABLE IF EXISTS tasks")
    cursor.execute("DROP TABLE IF EXISTS sprints")
    cursor.execute("DROP TABLE IF EXISTS epics")
    cursor.execute("DROP TABLE IF EXISTS user_team")
    cursor.execute("DROP TABLE IF EXISTS teams")
    cursor.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    cursor.close()
    conn.close()
    print("[DROP] All tables dropped.")

def insert_sample_data():
    conn = connect()
    cursor = conn.cursor()

    # --- Insert Sample Users ---
    users_data = [
        ("hsmith", "password123", "Harrison Smith", "harrison@hsmith.dev"),
        ("shancock", "password123", "Sam Hancock", "samuel.hancock.3@gmail.com")
    ]
    for user in users_data:
        cursor.execute("INSERT INTO users (username, password, full_name, email) VALUES (%s, %s, %s, %s)", user)

    # --- Insert Sample Teams ---
    teams_data = [
        ("Projects Together", "Primary team"),
        ("Harrison's Projects", "Personal Team"),
        ("Sam's Projects", "Personal Team")
    ]
    for team in teams_data:
        cursor.execute("INSERT INTO teams (name, description) VALUES (%s, %s)", team)

    # --- Map Users to Teams ---
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    user_ids = {username: id for id, username in users}
    cursor.execute("SELECT id, name FROM teams")
    teams = cursor.fetchall()
    team_ids = {name: id for id, name in teams}

    # Example mapping: (adjust as needed)
    # Map hsmith to "Projects Together"; shancock to "Projects Together" and "Sam's Projects".
    cursor.execute("INSERT INTO user_team (user_id, team_id) VALUES (%s, %s)", (user_ids["hsmith"], team_ids["Projects Together"]))
    cursor.execute("INSERT INTO user_team (user_id, team_id) VALUES (%s, %s)", (user_ids["shancock"], team_ids["Projects Together"]))
    cursor.execute("INSERT INTO user_team (user_id, team_id) VALUES (%s, %s)", (user_ids["shancock"], team_ids["Sam's Projects"]))

    # --- Insert Sample Epics ---
    epic_data = [
        ("Website Redesign", "Revamp the corporate website with a modern look.", "2023-01-01", "2023-03-31"),
        ("Mobile App Launch", "Develop and launch the new mobile application.", "2023-04-01", "2023-06-30")
    ]
    for epic in epic_data:
        # For epics, assign them to "Projects Together" and created by hsmith.
        cursor.execute("""
            INSERT INTO epics (name, description, start_date, end_date, user_id, team_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (epic[0], epic[1], epic[2], epic[3], user_ids["hsmith"], team_ids["Projects Together"]))

    cursor.execute("SELECT id, name FROM epics")
    epics = cursor.fetchall()
    epic_ids = {name: id for id, name in epics}

    # --- Insert Sample Sprints ---
    sprint_data = [
        ("Sprint 1", "Initial design and prototype development", "2023-01-01", "2023-01-14", epic_ids["Website Redesign"]),
        ("Sprint 2", "UI refinements and usability testing", "2023-01-15", "2023-01-28", epic_ids["Website Redesign"]),
        ("Sprint 1", "Core functionality and API integration", "2023-04-01", "2023-04-14", epic_ids["Mobile App Launch"]),
        ("Sprint 2", "Beta testing and performance optimization", "2023-04-15", "2023-04-28", epic_ids["Mobile App Launch"])
    ]
    for sprint in sprint_data:
        # For sprints, assign them to "Projects Together" and created by hsmith.
        cursor.execute("""
            INSERT INTO sprints (title, description, start_date, end_date, epic_id, user_id, team_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (sprint[0], sprint[1], sprint[2], sprint[3], sprint[4], user_ids["hsmith"], team_ids["Projects Together"]))

    cursor.execute("SELECT id, title, epic_id FROM sprints")
    sprints = cursor.fetchall()
    sprint_ids = {}
    for sprint in sprints:
        sprint_id, title, epic_id = sprint
        key = f"{title} - {epic_id}"
        sprint_ids[key] = sprint_id

    # --- Insert Sample Tasks ---
    task_data = [
        ("Design Homepage", "Create a modern homepage design", "2023-01-10", "Completed", "Design", "High", "None", None, sprint_ids.get(f"Sprint 1 - {epic_ids['Website Redesign']}")),
        ("Develop Contact Form", "Implement the contact form with validation", "2023-01-12", "In Progress", "Development", "Medium", "None", None, sprint_ids.get(f"Sprint 1 - {epic_ids['Website Redesign']}")),
        ("Test Responsive Layout", "Ensure the website works on all devices", "2023-01-20", "Pending", "QA", "Low", "None", None, sprint_ids.get(f"Sprint 2 - {epic_ids['Website Redesign']}")),
        ("Set Up Backend", "Configure server and database for the app", "2023-04-05", "Completed", "Development", "High", "None", None, sprint_ids.get(f"Sprint 1 - {epic_ids['Mobile App Launch']}")),
        ("Collect Beta Feedback", "Gather user feedback from beta testing", "2023-04-20", "Pending", "Research", "Medium", "None", None, sprint_ids.get(f"Sprint 2 - {epic_ids['Mobile App Launch']}"))
    ]
    for task in task_data:
        # For tasks, assign them to hsmith and "Projects Together".
        cursor.execute("""
            INSERT INTO tasks (title, description, due_date, status, category, priority, recurrence, parent_task_id, sprint_id, user_id, team_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (task[0], task[1], task[2], task[3], task[4], task[5], task[6], task[7], task[8], user_ids["hsmith"], team_ids["Projects Together"]))

    # --- Insert Sample Task Sessions ---
    task_session_data = [
        (1, "2023-01-05 09:00:00", "2023-01-05 10:30:00", 90),
        (1, "2023-01-06 14:00:00", "2023-01-06 15:00:00", 60),
        (2, "2023-01-11 09:00:00", None, 0),
        (4, "2023-04-04 13:00:00", "2023-04-04 15:00:00", 120)
    ]
    for session in task_session_data:
        cursor.execute("""
            INSERT INTO task_sessions (task_id, start_time, end_time, elapsed_time)
            VALUES (%s, %s, %s, %s)
        """, session)

    # --- Insert Sample Bugs ---
    bug_data = [
        ("Validation Error", "Form validation fails when email is missing.", "Open", "2023-01-11 10:00:00", None, 2),
        ("Layout Breaks on Mobile", "The layout breaks on small screen sizes.", "Open", "2023-01-18 09:30:00", None, None),
        ("Data Not Saving", "Beta feedback data is not saved in the database.", "Resolved", "2023-04-21 11:00:00", "2023-04-22 16:00:00", 5)
    ]
    for bug in bug_data:
        # For bugs, assign them to hsmith and "Projects Together".
        cursor.execute("""
            INSERT INTO bugs (title, description, status, created_date, resolved_date, task_id, user_id, team_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (bug[0], bug[1], bug[2], bug[3], bug[4], bug[5], user_ids["hsmith"], team_ids["Projects Together"]))

    # --- Insert Sample Notes ---
    note_data = [
        ("Revise color scheme and typography", "epic", epic_ids["Website Redesign"]),
        ("Discuss initial design concepts", "sprint", sprint_ids.get(f"Sprint 1 - {epic_ids['Website Redesign']}")),
        ("Update homepage layout after feedback", "task", 1),
        ("Investigate validation error on contact form", "bug", 1)
    ]
    for note in note_data:
        # For notes, assign them to hsmith and "Projects Together".
        cursor.execute("""
            INSERT INTO notes (note, note_type, reference_id, user_id, team_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (note[0], note[1], note[2], user_ids["hsmith"], team_ids["Projects Together"]))

    # --- Insert Sample Documents ---
    cursor.execute("SELECT id, note FROM notes")
    notes = cursor.fetchall()
    note_ids = {note_text: id for id, note_text in notes}
    document_data = [
        (note_ids["Revise color scheme and typography"], "color_scheme.pdf", "application/pdf", b"%PDF-1.4 sample pdf content here..."),
        (note_ids["Discuss initial design concepts"], "design_meeting.txt", "text/plain", b"Meeting notes: Discussed initial design ideas and feedback...")
    ]
    for doc in document_data:
        # For documents, assign them to hsmith and "Projects Together".
        cursor.execute("""
            INSERT INTO documents (note_id, filename, mimetype, document_blob, user_id, team_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (doc[0], doc[1], doc[2], doc[3], user_ids["hsmith"], team_ids["Projects Together"]))

    conn.commit()
    cursor.close()
    conn.close()
    print("[SAMPLE DATA] Sample data inserted successfully.")

if __name__ == "__main__":
    drop()
    setup()
    insert_sample_data()
