# trasker_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Task, Team
from .forms import TaskForm # You'll create a TaskForm in forms.py


@login_required # This ensures only logged-in users can access this view
def app_home_view(request):
    # You can add logic here later to fetch data for the dashboard
    # For now, it just renders a template.
    context = {
        'username': request.user.username,
    }
    return render(request, 'trasker_app/app_home.html', context)


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


