from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Note, Project, ProjectMembership, Task, User

# Text to put at the end of each page's <title>.
admin.site.site_title = _("Minitask administration")
# Text to put in each page's <h1> (and above login form).
admin.site.site_header = _("Minitask administration")
# Text to put at the top of the admin index page.
admin.site.index_title = None

admin.site.register(User, UserAdmin)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Note)
admin.site.register(ProjectMembership)
