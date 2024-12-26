# tasks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create_task/', views.create_task, name='create_task'),
    path('create_sub_tasks/', views.create_sub_tasks, name='create_sub_tasks')
]
