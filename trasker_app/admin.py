from django.contrib import admin
from .models import Team, Project, WorkWeek, Task, Issue, Note, Document, TaskSession # Import all your models

admin.site.register(Team)
admin.site.register(Project)
admin.site.register(WorkWeek)
admin.site.register(Task)
admin.site.register(Issue)
admin.site.register(Note)
admin.site.register(Document)
admin.site.register(TaskSession)
# You can customize how models appear in the admin later if needed