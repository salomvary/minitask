from django.contrib import admin

from .models import Project, Task, Note, ProjectMembership

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Note)
admin.site.register(ProjectMembership)
