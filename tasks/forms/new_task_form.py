from django.forms import DateInput, ModelForm

from tasks.models import Task


class NewTaskForm(ModelForm):
    def __init__(self, *args, project_choices, assignee_choices, **kwargs):
        super(NewTaskForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

        # TODO: There should be a better way of doing this,
        # maybe look at limit_choices_to:
        # https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.ForeignKey.limit_choices_to
        self.fields["project"].choices = project_choices or []
        self.fields["assignee"].choices = assignee_choices or []

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
