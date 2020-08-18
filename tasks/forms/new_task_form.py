from django.forms import DateInput, ModelForm

from tasks.models import Task


class NewTaskForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewTaskForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Task
        fields = (
            "project",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "assignee",
        )
        widgets = {
            "due_date": DateInput(
                # ISO date must be used with <input type=date> all times
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
        }
