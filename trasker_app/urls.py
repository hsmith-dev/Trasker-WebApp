# trasker_app/urls.py
from django.urls import path
from . import views

app_name = 'trasker_app'
urlpatterns = [
    path('', views.app_home_view, name='app_home'),
    # other app-specific paths
]