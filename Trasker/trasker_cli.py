import argparse
import sys
from trasker_psql import Trasker

# Instantiate a Trasker object.
trasker = Trasker()


def get_teams_for_user(user_id):
    """
    Retrieve a list of teams for the given user.
    Assumes that the Trasker.db_execute() method is available and that the schema for teams and user_team is set up.
    """
    query = """
        SELECT t.id, t.name 
        FROM teams t 
        JOIN user_team ut ON t.id = ut.team_id 
        WHERE ut.user_id = ?
    """
    return trasker.db_execute(query, (user_id,), fetch=True)


def login(username, password):
    """
    Log in the user using the provided credentials.
    Sets trasker.current_user to the user tuple and sets trasker.current_team to the first team (if any).
    """
    user = trasker.verify_user(username, password)
    if not user:
        print("Invalid username or password.")
        sys.exit(1)
    trasker.current_user = user  # e.g., (id, username, full_name, email)
    teams = get_teams_for_user(user[0])
    if teams:
        # Set default team to the first team in the list.
        trasker.current_team = teams[0]  # e.g., (team_id, team_name)
    else:
        trasker.current_team = None
    print(f"Logged in as {user[1]}. Default team: {trasker.current_team[1] if trasker.current_team else 'None'}")


def main():
    parser = argparse.ArgumentParser(description="Trasker: Task Manager CLI (Multi‑User Support)")

    # ----- Authentication -----
    parser.add_argument("--login", nargs=2, metavar=("username", "password"), help="Login with username and password")

    # ----- Task Management -----
    parser.add_argument("--quickAdd", nargs=3, metavar=("title", "description", "due_date"),
                        help="Add a quick task")
    parser.add_argument("--add", nargs=8, metavar=("title", "description", "due_date", "status",
                                                   "category", "priority", "recurrence", "parent_task_id"),
                        help="Add a detailed task")
    parser.add_argument("--list", action="store_true", help="List all active tasks")
    parser.add_argument("--listCategory", nargs=1, metavar="category", help="List tasks in a category")
    parser.add_argument("--listPriority", nargs=1, metavar="priority", help="List tasks by priority")
    parser.add_argument("--listStatus", nargs=1, metavar="status", help="List tasks by status")
    parser.add_argument("--listSub", nargs=1, metavar="parent_task_id", help="List subtasks of a parent task")
    parser.add_argument("--listDateFrame", nargs=2, metavar=("start_date", "end_date"),
                        help="List tasks between dates")
    parser.add_argument("--listAll", action="store_true", help="List all tasks")
    parser.add_argument("--search", nargs=1, metavar="keyword", help="Search tasks by keyword")
    parser.add_argument("--complete", metavar="task_id", type=int, help="Mark a task as complete")
    parser.add_argument("--changeStatus", nargs=2, metavar=("task_id", "status"),
                        help="Change task's status")
    parser.add_argument("--deleteById", metavar="task_id", type=int, help="Delete a task")
    parser.add_argument("--changeTitle", nargs=2, metavar=("task_id", "title"), help="Change task title")
    parser.add_argument("--changeDescription", nargs=2, metavar=("task_id", "description"),
                        help="Change task description")
    parser.add_argument("--changeCategory", nargs=2, metavar=("task_id", "category"),
                        help="Change task category")
    parser.add_argument("--changePriority", nargs=2, metavar=("task_id", "priority"),
                        help="Change task priority")

    # ----- Sprint Management -----
    parser.add_argument("--createSprint", nargs=3, metavar=("title", "description", "start_date"),
                        help="Create a sprint")
    parser.add_argument("--listSprints", action="store_true", help="List all sprints")
    parser.add_argument("--assignToSprint", nargs=2, metavar=("task_id", "sprint_id"),
                        help="Assign task to sprint")
    parser.add_argument("--listSprintTasks", nargs=1, metavar="sprint_id",
                        help="List tasks in a sprint")

    # ----- Task Time Tracking -----
    parser.add_argument("--startTimer", metavar="task_id", type=int, help="Start time tracking for a task")
    parser.add_argument("--stopTimer", metavar="task_id", type=int, help="Stop time tracking for a task")
    parser.add_argument("--elapsedTime", metavar="task_id", type=int, help="Get total elapsed time for a task")

    # ----- Bugs Management -----
    parser.add_argument("--listBugs", action="store_true", help="List all bugs")
    parser.add_argument("--listBugsByTask", nargs=1, metavar="task_id", help="List bugs for a given task")
    parser.add_argument("--addBug", nargs=5, metavar=("title", "description", "status", "created_date", "task_id"),
                        help="Add a bug")
    parser.add_argument("--changeBugStatus", nargs=2, metavar=("bug_id", "status"),
                        help="Change the status of a bug")
    parser.add_argument("--deleteBug", metavar="bug_id", type=int, help="Delete a bug")

    # ----- Notes Management -----
    parser.add_argument("--addNote", nargs=3, metavar=("note", "note_type", "reference_id"), help="Add a note")
    parser.add_argument("--listNotes", nargs=2, metavar=("note_type", "reference_id"),
                        help="List notes by type and reference id")
    parser.add_argument("--deleteNote", metavar="note_id", type=int, help="Delete a note")

    # ----- Documents Management -----
    parser.add_argument("--addDocument", nargs=4, metavar=("note_id", "filename", "mimetype", "filepath"),
                        help="Add a document linked to a note")

    args = parser.parse_args()

    # Process login first.
    if args.login:
        username, password = args.login
        login(username, password)
    else:
        print("Login required for multi-user support. Use --login username password")
        sys.exit(1)

    # ----- Process Task Management Commands -----
    if args.add:
        trasker.add_task(*args.add)
    elif args.quickAdd:
        trasker.add_task(*args.quickAdd,
                         status="Pending", category="Uncategorized",
                         priority="Medium", recurrence="None", parent_task_id=None)
    elif args.list:
        trasker.print_tasks(trasker.list_tasks())
    elif args.listCategory:
        trasker.print_tasks(trasker.list_category_tasks(args.listCategory[0]))
    elif args.listPriority:
        trasker.print_tasks(trasker.list_priority_tasks(args.listPriority[0]))
    elif args.listStatus:
        trasker.print_tasks(trasker.list_status_tasks(args.listStatus[0]))
    elif args.listSub:
        trasker.print_tasks(trasker.list_sub_tasks(args.listSub[0]))
    elif args.listDateFrame:
        trasker.print_tasks(trasker.search_task_by_dateframe(args.listDateFrame[0], args.listDateFrame[1]))
    elif args.listAll:
        trasker.print_tasks(trasker.list_all_tasks())
    elif args.search:
        trasker.print_tasks(trasker.search_task_by_keyword(args.search[0]))
    elif args.complete:
        trasker.task_mark_completed(args.complete)
    elif args.changeStatus:
        trasker.task_change_status(args.changeStatus[0], args.changeStatus[1])
    elif args.deleteById:
        trasker.delete_task(args.deleteById)
    elif args.changeTitle:
        trasker.task_change_title(args.changeTitle[0], args.changeTitle[1])
    elif args.changeDescription:
        trasker.task_change_description(args.changeDescription[0], args.changeDescription[1])
    elif args.changeCategory:
        trasker.task_change_category(args.changeCategory[0], args.changeCategory[1])
    elif args.changePriority:
        trasker.task_change_priority(args.changePriority[0], args.changePriority[1])

    # ----- Process Sprint Management Commands -----
    elif args.createSprint:
        trasker.create_sprint(*args.createSprint)
    elif args.listSprints:
        trasker.print_sprints()
    elif args.assignToSprint:
        trasker.assign_task_to_sprint(args.assignToSprint[0], args.assignToSprint[1])
    elif args.listSprintTasks:
        trasker.print_tasks(trasker.list_sprint_tasks(args.listSprintTasks[0]))

    # ----- Process Task Time Tracking Commands -----
    elif args.startTimer:
        trasker.start_task_timer(args.startTimer)
    elif args.stopTimer:
        trasker.stop_task_timer(args.stopTimer)
    elif args.elapsedTime:
        elapsed_time = trasker.get_total_task_time(args.elapsedTime)
        print(f"Total Time Spent on Task {args.elapsedTime}: {elapsed_time} seconds")

    # ----- Process Bugs Management Commands -----
    elif args.listBugs:
        bugs = trasker.list_all_bugs()
        if bugs:
            for bug in bugs:
                print(bug)
        else:
            print("No bugs found.")
    elif args.listBugsByTask:
        bugs = trasker.list_bugs_by_task(args.listBugsByTask[0])
        if bugs:
            for bug in bugs:
                print(bug)
        else:
            print("No bugs found for that task.")
    elif args.addBug:
        # Expecting: title, description, status, created_date, task_id
        trasker.db_execute(
            "INSERT INTO bugs (title, description, status, created_date, resolved_date, task_id, user_id, team_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (args.addBug[0], args.addBug[1], args.addBug[2], args.addBug[3], None, args.addBug[4],
             trasker.current_user[0] if trasker.current_user else None,
             trasker.current_team[0] if trasker.current_team else None)
        )
    elif args.changeBugStatus:
        trasker.db_execute(
            "UPDATE bugs SET status = ? WHERE id = ?",
            (args.changeBugStatus[1], args.changeBugStatus[0])
        )
    elif args.deleteBug:
        trasker.db_execute("DELETE FROM bugs WHERE id = ?", (args.deleteBug,))

    # ----- Process Notes Management Commands -----
    elif args.addNote:
        trasker.add_note(args.addNote[0], args.addNote[1], args.addNote[2])
    elif args.listNotes:
        trasker.print_notes(trasker.list_notes(args.listNotes[0], args.listNotes[1]))
    elif args.deleteNote:
        trasker.delete_note(args.deleteNote)

    # ----- Process Documents Management Commands -----
    elif args.addDocument:
        filepath = args.addDocument[3]
        try:
            with open(filepath, "rb") as f:
                document_blob = f.read()
        except Exception as e:
            print(f"Failed to read file: {e}")
            return
        trasker.add_document(args.addDocument[0], args.addDocument[1], args.addDocument[2], document_blob)

    trasker.close()


if __name__ == "__main__":
    main()
