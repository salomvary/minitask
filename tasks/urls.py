from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tasks/new', views.new_task, name='new'),
    path('tasks', views.create_task, name='create'),
    path('tasks/<int:task_id>/edit', views.edit_task, name='edit'),
    path('tasks/<int:task_id>', views.task_detail, name='detail'),
]
