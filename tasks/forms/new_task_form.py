from django.contrib.auth.models import User
from django.forms import DateInput, ModelForm
from django.conf import settings

from tasks.models import Project, Task

from ..templatetags.tasks_extras import user_str


class NewTaskForm(ModelForm):
    def __init__(self, *args, user, initial=None, **kwargs):
        # Set initial assignee when required
        if settings.REQUIRE_ASSIGNEE:
            initial = initial.copy() if initial else {}
            initial["assignee"] = user.id

        super(NewTaskForm, self).__init__(*args, initial=initial, **kwargs)

        # Make all widgets look like Bootstrap form controls
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

        # TODO: There should be a better way of doing this,
        # maybe look at limit_choices_to:
        # https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.ForeignKey.limit_choices_to
        projects = Project.objects.visible_to_user(user)
        project_choices = [(project.id, str(project)) for project in projects]
        assignee_choices = [(user.id, user_str(user)) for user in User.objects.all()]
        self.fields["project"].choices = [("", "")] + (project_choices or [])
        self.fields["assignee"].choices = [("", "")] + (assignee_choices or [])

        # Some fields can be configured to be required
        self.fields["due_date"].required = settings.REQUIRE_DUE_DATE
        self.fields["assignee"].required = settings.REQUIRE_ASSIGNEE

    class Meta:
        model = Task
        fields = (
            "version",
            "project",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "assignee",
            "tags",
        )
        widgets = {
            "due_date": DateInput(
                # ISO date must be used with <input type=date> all times
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
        }
