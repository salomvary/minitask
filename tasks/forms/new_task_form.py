from django.forms import DateInput, ModelForm

from tasks.models import Task


class NewTaskForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewTaskForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Task
        fields = ("project", "title", "description", "status", "due_date", "assignee")
        widgets = {
            "due_date": DateInput(attrs={"type": "date"}),
        }
