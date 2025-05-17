from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name='team_members')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Formerly Epics
class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    assignees = models.ManyToManyField(User, related_name='assigned_projects', blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Formerly Sprints
class WorkWeek(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='work_weeks')
    assignees = models.ManyToManyField(User, related_name='assigned_work_weeks', blank=True)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='work_weeks')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Archived', 'Archived'),
        ('Cancelled', 'Cancelled'),
        ('Holding', 'Holding'),
        ('Failed', 'Failed'),
    ]
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Low')
    recurrence = models.CharField(max_length=50, default="None", blank=True)

    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    workweek = models.ForeignKey('WorkWeek', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks') # Use 'WorkWeek' directly.

    assignees = models.ManyToManyField(User, related_name='assigned_tasks', blank=True) # CRITICAL CHANGE: Replaced ForeignKey 'user' with ManyToManyField 'assignees'
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks') # Added blank=True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class TaskSession(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    elapsed_time = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session for {self.task.title} at {self.start_time}"

# Formerly Bugs
class Issue(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    # created_date_issue is effectively handled by created_at
    resolved_date_issue = models.DateTimeField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    assignees = models.ManyToManyField(User, related_name='assigned_issues', blank=True)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Note(models.Model):
    NOTE_TYPE_CHOICES = [
        ('Project', 'Project'),
        ('WorkWeek', 'WorkWeek'),
        ('Task', 'Task'),
        ('Issue', 'Issue'),
        ('General', 'General')
    ]

    note = models.TextField()
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE_CHOICES, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_notes')
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_notes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.note[:50] + "..."

class Document(models.Model): # Singular model name convention
    note = models.ForeignKey(Note, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=100, blank=True, null=True)
    document_file = models.FileField(upload_to='documents/%Y/%m/%d/')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents')
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_documents')
    # upload_date is effectively created_at
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename