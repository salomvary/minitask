from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Note, Project, ProjectMembership, Task, User

admin.site.register(User, UserAdmin)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Note)
admin.site.register(ProjectMembership)
