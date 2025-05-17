# trasker_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Task, Team
from .forms import TaskForm # You'll create a TaskForm in forms.py

@login_required
def add_task_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            # task.user = request.user # If assigning to current user
            # Logic to get current_team (e.g., from session or user profile)
            # current_team_id = request.session.get('current_team_id')
            # if current_team_id:
            #    task.team = Team.objects.get(id=current_team_id)
            task.save()
            return redirect('some_view_name_to_show_tasks') # Redirect after POST
    else:
        form = TaskForm()
    return render(request, 'trasker_app/add_task_form.html', {'form': form})